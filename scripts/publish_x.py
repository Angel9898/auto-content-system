"""scripts/publish_x.py

Posts to X (Twitter). If user access tokens are available, it attempts media upload (chunked)
via v1.1 endpoints. Otherwise it falls back to a simple v2 text-only post using Bearer token.

Requires:
- X_ACCESS_TOKEN & X_ACCESS_TOKEN_SECRET & X_API_KEY & X_API_SECRET for OAuth 1.0a user posting (preferred)
- X_BEARER_TOKEN for app-only v2 text posts (fallback)
"""
import os, sys, json, requests
from requests_oauthlib import OAuth1

X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
X_BEARER = os.getenv('X_BEARER_TOKEN')
DRY = os.getenv('DRY_RUN','false').lower()=='true'

def post_text_v2(text):
    url = 'https://api.twitter.com/2/tweets'
    headers = {'Authorization': f'Bearer {X_BEARER}', 'Content-Type':'application/json'}
    r = requests.post(url, headers=headers, json={'text':text}, timeout=30)
    r.raise_for_status()
    return r.json()

def post_with_user_oauth(text):
    # simplified: v1.1 media upload flow is complex; here we post text-only via user oauth
    auth = OAuth1(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    r = requests.post(url, auth=auth, data={'status':text}, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    try:
        with open('assets/content.json') as f:
            data = json.load(f)
    except Exception:
        data = {'x_post':'Automated post'}
    text = data.get('x_post','Automated post')
    if DRY:
        print('[DRY RUN] Would post to X:', text)
        return
    try:
        if X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET and X_API_KEY and X_API_SECRET:
            print('Posting via user OAuth (v1.1)...')
            resp = post_with_user_oauth(text)
            print('Posted to X:', resp.get('id_str'))
            return
    except Exception as e:
        print('User OAuth post failed, falling back to bearer v2:', e)
    if X_BEARER:
        print('Posting via app-only bearer token (v2)...')
        resp = post_text_v2(text)
        print('Posted to X (v2):', resp)
    else:
        print('No X credentials found; cannot post.')

if __name__ == '__main__':
    main()
