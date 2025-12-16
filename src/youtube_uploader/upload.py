# @title 6. Auto-Upload to YouTube
# ⚠️ Prerequisite: You must have 'token.json' in your Drive folder.

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_video_to_youtube(video_file_path, meta_data):
    
    # Path to your token file in Drive
    TOKEN_PATH = "src\\youtube_uploader\\token.json" 

    # Metadata for the video
    VIDEO_TITLE = meta_data.get("title")
    VIDEO_DESC = meta_data.get("description")
    TAGS = meta_data.get("tags")
    CATEGORY_ID = meta_data.get("category_id")
    
    
    if not os.path.exists(TOKEN_PATH):
        print(f"❌ Error: token.json not found at {TOKEN_PATH}")
        print("Please run the local script to generate it first.")
        return

    if not os.path.exists(video_file_path):
        print(f"❌ Error: Video file not found at {video_file_path}")
        return

    print("🔑 Authenticating with YouTube...")
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_PATH)
        youtube = build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Auth Failed: {e}")
        print("Try re-generating token.json locally.")
        return

    print(f"📤 Uploading: {VIDEO_TITLE}...")
    
    body = {
        'snippet': {
            'title': VIDEO_TITLE,
            'description': VIDEO_DESC,
            'tags': TAGS,
            'categoryId': CATEGORY_ID
        },
        'status': {
            'privacyStatus': 'private', # Start private to check for copyright issues first
            'selfDeclaredMadeForKids': False # Set True if strictly for kids app
        }
    }

    # Resumable upload (reliable for Colab)
    media = MediaFileUpload(video_file_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   🚀 Uploading... {int(status.progress() * 100)}%")
            
    print(f"✅ Upload Complete! Video ID: {response.get('id')}")
    print(f"🔗 Link: https://youtu.be/{response.get('id')}")