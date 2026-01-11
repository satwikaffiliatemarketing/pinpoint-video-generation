import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta, timezone

def get_authenticated_service():
    """Authenticates and returns the YouTube service."""
    
    # We expect these to be set in environment variables (Github Secrets)
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    
    if not all([refresh_token, client_id, client_secret]):
        print("Error: Missing YouTube OAuth environment variables.")
        return None

    creds = Credentials(
        None, # No access token initially
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_video(video_path, data):
    """
    Uploads the video to YouTube with SEO metadata.
    data format expected: { "date": "YYYY-MM-DD", "answer": "..." }
    """
    youtube = get_authenticated_service()
    if not youtube:
        return False

    # Date Logic: Ensure we use the date from the API or IST
    date_str = data.get("date")
    # Convert '2026-01-11' to 'Jan 11, 2026'
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%b %d, %Y")
    except:
        formatted_date = date_str

    title = f"LinkedIn Pinpoint {formatted_date} Answer | Today's Pinpoint Hints & Key"
    
    # Description
    description = f"""
LinkedIn Pinpoint Answer for {formatted_date}.
See the full solution and archives here: https://wordsolverx.com/pinpoint-solver

Today's LinkedIn Pinpoint answer is revealed in this video along with the clues.

#LinkedInPinpoint #PinpointGame #DailyPuzzle #WordGame
    """

    body = {
        "snippet": {
            "title": title,
            "description": description.strip(),
            "tags": ["LinkedIn Pinpoint", "Pinpoint Answer", "Daily Puzzle", "Word Game", "Pinpoint Hints"],
            "categoryId": "20" # Gaming
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    try:
        print(f"Uploading {video_path}...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = request.execute()
        print(f"Upload Successful! Video ID: {response['id']}")
        return True
    except Exception as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return False
