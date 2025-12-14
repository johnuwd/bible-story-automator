# @title 6. Auto-Upload to YouTube
# ⚠️ Prerequisite: You must have 'token.json' in your Drive folder.

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


TOPIC = "The Story of Joseph and his Coat"


# --- CONFIG ---
# Path to your token file in Drive
TOKEN_PATH = "token.json" 

# Metadata for the video
VIDEO_TITLE = f"{TOPIC} - Telugu Bible Story (AI Animation)"
VIDEO_DESC = """
This is a bible story generated using AI Tools.
#Bible #Telugu #Christian #AI #Shorts
"""
TAGS = ["Bible", "Telugu", "Christian", "Jesus", "AI Animation"]
CATEGORY_ID = "22" # 22 = People & Blogs

def upload_video_to_youtube(video_file_path):
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
            'privacyStatus': 'public', # Start private to check for copyright issues first
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

# --- EXECUTE UPLOAD ---
# This uses the output path from your previous step
output_path = "The_Story_of_Joseph_and_his_Coat_Telugu.mp4"
upload_video_to_youtube(output_path)