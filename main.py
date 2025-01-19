from tiktok_downloader import download_tiktok_clips
from youtube_uploader import process_and_upload_clips
from logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    try:
        TIKTOK_USERNAME = "your_tiktok_username"  # Replace with your TikTok username
        DOWNLOAD_DIR = "./tiktok_downloads"
        download_tiktok_clips(TIKTOK_USERNAME, DOWNLOAD_DIR)
        process_and_upload_clips(DOWNLOAD_DIR)
    except Exception as e:
        import logging
        logging.error(f"An unexpected error occurred in the process: {e}")
