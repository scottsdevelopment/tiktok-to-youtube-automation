import os
import shutil
import logging
import pyktok as pyk

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


def download_tiktok_clips(username, download_dir):
    """Download TikTok clips and metadata."""
    try:
        os.makedirs(download_dir, exist_ok=True)
        logging.info(f"Downloading TikTok videos for user: {username}")
        
        pyk.specify_browser("edge")
        
        pyk.save_tiktok_multi_page(
            username,
            ent_type='user',
            save_video=True,
            metadata_fn=os.path.join(download_dir, 'metadata.csv')
        )
        
        move_videos_to_download_dir(os.getcwd(), download_dir)

        logging.info(f"TikTok clips and metadata downloaded successfully to {download_dir}.")

    except PermissionError as e:
        logging.error(f"Permission denied for directory {download_dir}: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during download: {e}")
