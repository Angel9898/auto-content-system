"""helpers/validate_payloads.py

Validators used when SELF_TEST is enabled. They check that generated assets exist
and that platform payloads meet basic constraints (lengths, keys present).
"""
import json
import os

def validate_all_payloads():
    # Check content.json exists
    if not os.path.exists('assets/content.json'):
        raise AssertionError('assets/content.json missing')
    with open('assets/content.json') as f:
        data = json.load(f)
    # LinkedIn post check
    if 'linkedin_post' not in data or len(data['linkedin_post']) < 50:
        raise AssertionError('linkedin_post missing or too short')
    # X post check
    if 'x_post' not in data or len(data['x_post']) > 280:
        raise AssertionError('x_post missing or too long')
    # Carousel check
    if 'ig_carousel' not in data or not isinstance(data['ig_carousel'], list) or len(data['ig_carousel'])==0:
        raise AssertionError('ig_carousel missing or empty')
    # Hashtags
    if 'hashtags' not in data or not isinstance(data['hashtags'], list):
        raise AssertionError('hashtags missing or wrong format')
    # Check media
    images = [f for f in os.listdir('assets') if f.endswith('.png') or f.endswith('.jpg')]
    if len(images) == 0:
        raise AssertionError('No images found in assets/')
    if not os.path.exists('assets/video_post.mp4'):
        raise AssertionError('assets/video_post.mp4 missing')
    print('All payload validators passed.')
