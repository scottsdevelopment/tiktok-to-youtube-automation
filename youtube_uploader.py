import os
import json
import logging
from googleapiclient.http import MediaFileUpload
from auth import get_authenticated_service

def upload_to_youtube(youtube, video_path, title, description):
    """Upload a video to YouTube."""
    try:
        logging.info(f"Uploading video: {video_path} with title: {title}")
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["TikTok", "Shorts", "Reels"],
                "categoryId": "22"  # People & Blogs category
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        response = request.execute()
        logging.info(f"Uploaded successfully: Video ID {response['id']}")
    except Exception as e:
        logging.error(f"Error uploading video: {e}")

def process_and_upload_clips(download_dir):
    """Process downloaded TikTok clips and upload them to YouTube."""
    try:
        youtube = get_authenticated_service()
        for filename in os.listdir(download_dir):
            if filename.endswith(".mp4"):
                video_path = os.path.join(download_dir, filename)
                metadata_path = video_path.replace(".mp4", ".json")

                # Extract metadata
                title = "TikTok Clip"
                description = "Uploaded from TikTok"
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as file:
                        metadata = json.load(file)
                        title = metadata.get("text", title)
                        description = f"Original TikTok: {metadata.get('webVideoUrl', '')}"

                # Upload to YouTube
                upload_to_youtube(youtube, video_path, title, description)
    except Exception as e:
        logging.error(f"An unexpected error occurred in the process: {e}")
