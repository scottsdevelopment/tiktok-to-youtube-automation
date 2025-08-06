import os
import csv
import logging
from googleapiclient.http import MediaFileUpload
from auth import get_authenticated_service

def upload_to_youtube(youtube, video_path, title, description):
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
        metadata_path = os.path.join(download_dir, 'metadata.csv')
        
        if not os.path.exists(metadata_path):
            logging.error(f"Metadata file not found: {metadata_path}")
            return
            
        with open(metadata_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                video_id = row['video_id']
                username = row['author_username']

                filename = f"@{username}_video_{video_id}.mp4"
                video_path = os.path.join(download_dir, filename)
                
                title = row.get("video_description") or f"TikTok by {username}"
                
                description = f"Credit to @{username} on TikTok."
                
                if os.path.exists(video_path):
                    upload_to_youtube(youtube, video_path, title, description)
                else:
                    logging.warning(f"Video file not found for ID {video_id}: {video_path}")

    except Exception as e:
        logging.error(f"An unexpected error occurred in the process: {e}")

