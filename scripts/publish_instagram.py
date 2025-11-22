"""scripts/publish_instagram.py

Publish carousel or single media to Instagram Business account via the Graph API.

Requires:
- FB_PAGE_ACCESS_TOKEN
- IG_USER_ID

Flow (simplified):
1. For each image, create a media container (POST /{ig-user-id}/media with image_url or image data)
2. POST /{ig-user-id}/media_publish with 'creation_id' or 'children' for carousels

NOTE: The Graph API expects publicly accessible image URLs or a Facebook-hosted image (upload to FB CDN). This script demonstrates the flow and includes fallbacks.
"""
import os, sys, json, requests

FB_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')
IG_USER = os.getenv('IG_USER_ID')
IMAGE_HOSTING = os.getenv('IMAGE_HOSTING_URL')  # optional: endpoint to upload images and return public URLs
DRY = os.getenv('DRY_RUN','false').lower()=='true'

def upload_image_hosting(local_path):
    """Optional helper to upload an image to a public hosting endpoint that returns an image URL.
    The repo does not include such an uploader; configure IMAGE_HOSTING to a service you control.
    """
    if not IMAGE_HOSTING:
        raise RuntimeError('No IMAGE_HOSTING configured')
    files = {'file': open(local_path,'rb')}
    r = requests.post(IMAGE_HOSTING, files=files, timeout=60)
    r.raise_for_status()
    return r.json().get('url')

def create_media_container(image_url):
    url = f'https://graph.facebook.com/v17.0/{IG_USER}/media'
    params = {'image_url': image_url, 'access_token': FB_TOKEN}
    r = requests.post(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get('id')

def publish_container(container_id):
    url = f'https://graph.facebook.com/v17.0/{IG_USER}/media_publish'
    params = {'creation_id': container_id, 'access_token': FB_TOKEN}
    r = requests.post(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    assets_dir = sys.argv[1] if len(sys.argv)>1 else 'assets'
    if not os.path.exists(assets_dir):
        print('Assets dir missing')
        return
    try:
        with open(os.path.join('assets','content.json')) as f:
            content = json.load(f)
    except Exception as e:
        print('content.json missing or invalid', e)
        return
    images = sorted([os.path.join(assets_dir,'images',f) for f in os.listdir(os.path.join(assets_dir,'images')) if f.endswith('.png') or f.endswith('.jpg')])
    if not images:
        print('No images to publish')
        return
    if DRY:
        print('[DRY RUN] Would create containers for images:', images)
        return
    if not (FB_TOKEN and IG_USER):
        print('Missing FB_PAGE_ACCESS_TOKEN or IG_USER_ID')
        return
    # upload images (either host them externally or use image hosting endpoint)
    container_ids = []
    for img in images:
        try:
            if IMAGE_HOSTING:
                image_url = upload_image_hosting(img)
            else:
                # Attempt to use a data URL via uploading to Graph API is not supported here.
                raise RuntimeError('No IMAGE_HOSTING configured. Please provide public URLs or implement FB CDN upload flow.')
            cid = create_media_container(image_url)
            container_ids.append(cid)
            print('Created container', cid)
        except Exception as e:
            print('Failed to create container for', img, e)
    if not container_ids:
        print('No containers created; aborting publish.')
        return
    # publish carousel
    try:
        # Graph API expects children param as comma-separated list of container ids
        child_list = ','.join(container_ids)
        publish_resp = requests.post(f'https://graph.facebook.com/v17.0/{IG_USER}/media_publish', params={'children': child_list, 'access_token': FB_TOKEN}, timeout=30)
        publish_resp.raise_for_status()
        print('Published Instagram carousel:', publish_resp.json())
    except Exception as e:
        print('Publish failed', e)

if __name__ == '__main__':
    main()
