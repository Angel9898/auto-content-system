"""scripts/publish_youtube.py

Upload video to YouTube using OAuth refresh token credentials. This script uses
google-api-python-client if available; otherwise it prints the intended actions.
Environment variables required:
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN

The script performs a resumable upload and uploads a thumbnail (assets/thumbnail.png).
"""
import os, sys
import json

def upload_with_google_client(video_file, title, description, tags):
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except Exception as e:
        print('google client libs not installed or import failed:', e)
        return False

    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
    if not (client_id and client_secret and refresh_token):
        print('YouTube credentials missing. Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN')
        return False

    creds = Credentials(token=None, refresh_token=refresh_token, token_uri='https://oauth2.googleapis.com/token', client_id=client_id, client_secret=client_secret, scopes=['https://www.googleapis.com/auth/youtube.upload'])
    youtube = build('youtube','v3',credentials=creds)
    body = {
        'snippet': {'title': title, 'description': description, 'tags': tags},
        'status': {'privacyStatus': 'public'}
    }
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print('Upload progress:', int(status.progress() * 100), '%')
    video_id = response.get('id')
    print('Uploaded video id:', video_id)
    # upload thumbnail
    thumb = 'assets/thumbnail.png'
    if os.path.exists(thumb):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumb)).execute()
        print('Thumbnail uploaded.')
    return True

def main():
    video_file = sys.argv[1] if len(sys.argv)>1 else 'assets/video_post.mp4'
    if not os.path.exists(video_file):
        print('Video file not found:', video_file)
        return
    # load metadata
    meta = {}
    try:
        with open('assets/content.json') as f:
            meta = json.load(f)
    except Exception:
        pass
    title = meta.get('title','Automated video')
    description = meta.get('linkedin_post','')
    tags = meta.get('hashtags',[])
    dry = os.getenv('DRY_RUN','false').lower()=='true'
    if dry:
        print('[DRY RUN] Would upload to YouTube:', video_file, title)
        return
    success = upload_with_google_client(video_file, title, description, tags)
    if not success:
        print('YouTube upload did not run. Ensure google client libs and credentials are set.')

if __name__ == '__main__':
    main()
