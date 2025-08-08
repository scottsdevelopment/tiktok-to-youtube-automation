import os
import csv
import json
import logging
from typing import Optional, Set

from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from auth import get_authenticated_service


YOUTUBE_TITLE_MAX = 100


class QuotaExceededError(Exception):
    """Raised when YouTube Data API quota is exceeded."""


def _ensure_upload_log(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tiktok_video_id", "youtube_video_id", "title"])


def _load_uploaded_ids(path: str) -> Set[str]:
    if not os.path.exists(path):
        return set()
    uploaded = set()
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid = (row.get("tiktok_video_id") or "").strip()
            if vid:
                uploaded.add(vid)
    return uploaded


def _append_upload_log(path: str, tiktok_id: str, youtube_id: str, title: str) -> None:
    _ensure_upload_log(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([tiktok_id, youtube_id, title])


def _sanitize_title(title: Optional[str], username: str, video_id: str) -> str:
    raw = (title or "").strip()
    if not raw:
        raw = f"TikTok by @{username} ({video_id})"

    # Collapse whitespace
    raw = " ".join(raw.split())

    # Hard cap to YouTube’s 100 char limit
    if len(raw) > YOUTUBE_TITLE_MAX:
        raw = raw[:YOUTUBE_TITLE_MAX]

    return raw


def _parse_reason_from_http_error(err: Exception) -> Optional[str]:
    # Works for HttpError and ResumableUploadError (which wraps HttpError)
    content = getattr(err, "content", None)
    if not content:
        return None
    try:
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")
        data = json.loads(content)
        # Typical shape: {"error":{"errors":[{"reason":"quotaExceeded", ...}], "code":403, "message":"..."}}
        errors = (
            data.get("error", {}).get("errors")
            or data.get("errors")
            or []
        )
        if errors and isinstance(errors, list):
            reason = errors[0].get("reason")
            return reason
        # Some variants only have "error": {"message": "..."}
        return None
    except Exception:
        return None


def upload_to_youtube(youtube, video_path: str, title: str, description: str) -> Optional[str]:
    """
    Returns YouTube video ID on success.
    Raises QuotaExceededError if quota is exceeded.
    Returns None for any other failure (and logs it).
    """
    try:
        logging.info("Uploading video: %s with title: %s", video_path, title)
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["TikTok", "Shorts", "Reels"],
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()  # will raise HttpError on 4xx/5xx
        yt_id = response["id"]
        logging.info("Uploaded successfully: Video ID %s", yt_id)
        return yt_id

    except Exception as e:
        # Detect quota exceeded specifically
        reason = _parse_reason_from_http_error(e)
        if reason == "quotaExceeded":
            logging.error(
                "YouTube quota exceeded. Stopping gracefully. "
                "Check your Cloud Console -> YouTube Data API v3 -> Quotas."
            )
            raise QuotaExceededError("YouTube Data API quota exceeded") from e

        # Keep going for everything else, but include full stack trace
        logging.exception("Error uploading video: %s", e)
        return None


def process_and_upload_clips(download_dir: str) -> None:
    """
    Reads tiktok metadata.csv in download_dir, skips already uploaded items
    recorded in youtube_uploads.csv, uploads the rest.

    Continues on non-quota errors; gracefully stops if quota is exceeded.
    """
    try:
        youtube = get_authenticated_service()
    except Exception as e:
        logging.exception("Failed to authenticate YouTube client: %s", e)
        return

    metadata_path = os.path.join(download_dir, "metadata.csv")
    upload_log_path = os.path.join(download_dir, "youtube_uploads.csv")

    if not os.path.exists(metadata_path):
        logging.error("Metadata file not found: %s", metadata_path)
        return

    uploaded_ids = _load_uploaded_ids(upload_log_path)
    logging.info("Loaded %d previously uploaded TikToks from %s", len(uploaded_ids), upload_log_path)

    try:
        with open(metadata_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                video_id = (row.get("video_id") or "").strip()
                username = (row.get("author_username") or "").strip()

                if not video_id or not username:
                    logging.warning("Skipping row with missing video_id/username: %s", row)
                    continue

                if video_id in uploaded_ids:
                    logging.info("Already uploaded TikTok %s; skipping.", video_id)
                    continue

                filename = f"@{username}_video_{video_id}.mp4"
                video_path = os.path.join(download_dir, filename)

                title = _sanitize_title(row.get("video_description"), username, video_id)
                description = f"Credit to @{username} on TikTok."

                if not os.path.exists(video_path):
                    logging.warning("Video file not found for ID %s: %s", video_id, video_path)
                    continue

                try:
                    youtube_id = upload_to_youtube(youtube, video_path, title, description)
                except QuotaExceededError:
                    # Graceful stop on quota, no stack trace beyond what's already logged
                    logging.error("Halting uploads due to quota limits. Last attempted TikTok: %s", video_id)
                    break  # exit the loop gracefully
                except Exception as e:
                    # As a safety net (shouldn’t happen often), keep going
                    logging.exception("Unexpected failure for TikTok %s: %s", video_id, e)
                    continue

                if youtube_id:
                    _append_upload_log(upload_log_path, video_id, youtube_id, title)
                    uploaded_ids.add(video_id)

    except Exception as e:
        logging.exception("An unexpected error occurred in the process: %s", e)
