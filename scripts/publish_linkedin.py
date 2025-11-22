"""scripts/publish_linkedin.py

Registers an image upload with LinkedIn, uploads binary to the returned uploadUrl via PUT,
and creates a UGC post referencing the asset.

Requires:
- LINKEDIN_ACCESS_TOKEN
- LI_OWNER_URN (e.g., 'urn:li:person:<id>' or 'urn:li:organization:<id>')
"""
import os, sys, json, requests

TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
OWNER = os.getenv('LI_OWNER_URN')
DRY = os.getenv('DRY_RUN','false').lower()=='true'

def register_upload(file_name, owner):
    url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type':'application/json'}
    body = {
        "registerUploadRequest": {
            "owner": owner,
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "serviceRelationships": [{"identifier":"urn:li:userGeneratedContent","relationshipType":"OWNER"}],
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
        }
    }
    r = requests.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json()

def upload_binary(upload_url, file_path):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type':'application/octet-stream'}
    with open(file_path,'rb') as f:
        r = requests.put(upload_url, headers=headers, data=f, timeout=60)
        r.raise_for_status()
    return True

def create_share(owner, asset_urn, text):
    url = 'https://api.linkedin.com/v2/ugcPosts'
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type':'application/json'}
    body = {
      "author": owner,
      "lifecycleState": "PUBLISHED",
      "specificContent": {
        "com.linkedin.ugc.ShareContent": {
          "shareCommentary": {"text": text},
          "shareMediaCategory": "IMAGE",
          "media": [
            {
              "status": "READY",
              "description": {"text": ""},
              "media": asset_urn,
              "title": {"text": "Image"}
            }
          ]
        }
      },
      "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    r = requests.post(url, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    assets_dir = sys.argv[1] if len(sys.argv)>1 else 'assets'
    if DRY:
        print('[DRY RUN] Would publish to LinkedIn')
        return
    if not (TOKEN and OWNER):
        print('Missing LINKEDIN_ACCESS_TOKEN or LI_OWNER_URN')
        return
    images = sorted([os.path.join(assets_dir,'images',f) for f in os.listdir(os.path.join(assets_dir,'images')) if f.endswith('.png') or f.endswith('.jpg')])
    if not images:
        print('No images found for LinkedIn.')
        return
    # register upload for the first image (example)
    info = register_upload(images[0], OWNER)
    upload_url = info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = info['value']['asset']
    print('Upload URL:', upload_url)
    upload_binary(upload_url, images[0])
    print('Uploaded binary to LinkedIn CDN.')
    # create post
    with open(os.path.join(assets_dir,'content.json')) as f:
        content = json.load(f)
    resp = create_share(OWNER, asset_urn, content.get('linkedin_post',''))
    print('LinkedIn post created:', resp)

if __name__ == '__main__':
    main()
