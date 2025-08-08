import os
import shutil
import logging
import pyktok as pyk
from urllib.parse import urlparse

def tiktok_url_to_filename(url: str) -> str:
    """
    Converts a TikTok video URL into a safe filename.
    """
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    
    if len(parts) >= 3 and parts[1] == "video":
        username = parts[0]
        video_id = parts[2]
        return f"{username}_video_{video_id}.mp4"
    
    raise ValueError("Invalid TikTok video URL format")

def move_videos_to_download_dir(root_dir, download_dir):
    """Moves all .mp4 files from the root directory to the download directory."""
    logging.info(f"Moving video files to {download_dir}...")
    logging.debug(f"Searching for .mp4 files in: {root_dir}")
    
    found_videos = False
    for filename in os.listdir(root_dir):
        if filename.endswith(".mp4"):
            found_videos = True
            source = os.path.join(root_dir, filename)
            destination = os.path.join(download_dir, filename)
            logging.debug(f"Found video: {source}")
            
            try:
                if os.path.exists(destination):
                    logging.warning(f"File {filename} already exists in destination. Skipping move.")
                    continue
                shutil.move(source, destination)
                logging.info(f"Moved {filename} to {download_dir}")
            except FileNotFoundError:
                logging.warning(f"Video file {source} not found, skipping move.")
            except Exception as e:
                logging.error(f"Failed to move file {filename}: {e}")

    if not found_videos:
        logging.info("No .mp4 files found in the root directory to move.")


async def download_tiktok_clips(username, download_dir):
    """Download TikTok clips and metadata."""
    try:
        os.makedirs(download_dir, exist_ok=True)
        logging.info(f"Downloading TikTok videos for user: {username}")
        
        video_list = await pyk.get_video_urls(
            username,
            ent_type='user',
            video_ct=500,
        )

        logging.info(f"Found {len(video_list)} videos for user {username}.")

        for video in video_list:
            try:
                filename = tiktok_url_to_filename(video)
                root_path = os.path.join(os.getcwd(), filename)
                download_path = os.path.join(download_dir, filename)

                if os.path.exists(root_path) or os.path.exists(download_path):
                    logging.info(f"Video already exists: {filename}. Skipping download.")
                    continue

                if video is None:
                    logging.warning("Received None for video URL, skipping.")
                    continue

                logging.info(f"Processing video: {video}")
                await pyk.save_tiktok(
                    video,
                    save_video=True,
                    metadata_fn=os.path.join(download_dir, "metadata.csv")
                )

                move_videos_to_download_dir(os.getcwd(), download_dir)

            except Exception as e:
                logging.error(f"Failed to download video {video}: {e}", exc_info=True)
                continue

        
     
        logging.info(f"TikTok clips and metadata downloaded successfully to {download_dir}.")

    except PermissionError as e:
        logging.error(f"Permission denied for directory {download_dir}: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during download: {e}")
