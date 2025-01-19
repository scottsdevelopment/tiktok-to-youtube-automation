import logging

def setup_logger():
    """Configure logging settings."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("tiktok_to_youtube.log"),
            logging.StreamHandler()
        ]
    )
