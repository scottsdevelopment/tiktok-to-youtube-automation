import os
import subprocess
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# TikTok Scraper Configuration
TIKTOK_USERNAME = "your_tiktok_username"  # Replace with your TikTok username
DOWNLOAD_DIR = "./tiktok_downloads"

# YouTube API Configuration
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "resources/client_secrets.json"  # Replace with your Google API credentials

def download_tiktok_clips(username, download_dir):
    """Download TikTok clips and metadata."""
    os.makedirs(download_dir, exist_ok=True)
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
    print("TikTok clips downloaded successfully!")

def get_authenticated_service():
    """Authenticate with YouTube Data API."""
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build("youtube", "v3", credentials=credentials)

def upload_to_youtube(youtube, video_path, title, description):
    """Upload a video to YouTube."""
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
    print(f"Uploaded: {response['id']}")

def process_and_upload_clips():
    """Download TikTok clips and upload them to YouTube."""
    # Step 1: Download TikTok Clips
    download_tiktok_clips(TIKTOK_USERNAME, DOWNLOAD_DIR)

    # Step 2: Authenticate with YouTube
    youtube = get_authenticated_service()

    # Step 3: Iterate through downloaded videos and upload to YouTube
    for filename in os.listdir(DOWNLOAD_DIR):
        if filename.endswith(".mp4"):
            video_path = os.path.join(DOWNLOAD_DIR, filename)
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

if __name__ == "__main__":
    process_and_upload_clips()
