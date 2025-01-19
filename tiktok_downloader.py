import os
import subprocess
import logging

def download_tiktok_clips(username, download_dir):
    """Download TikTok clips and metadata."""
    try:
        os.makedirs(download_dir, exist_ok=True)
        logging.info(f"Downloading TikTok videos for user: {username}")
        command = [
            "npx",
            "tiktok-scraper",
            "user",
            username,
            "-d",
            "-t",
            "json",
            "-n",
            "20",  # Adjust the number of clips to download
            "-p",
            download_dir
        ]
        subprocess.run(command, check=True)
        logging.info("TikTok clips downloaded successfully!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error downloading TikTok videos: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
