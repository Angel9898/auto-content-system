"""scripts/publish_all.py

High-level orchestrator that runs generation, assembly, then publishes to platforms.
Supports SELF_TEST mode which validates payloads without posting.
"""
import os, subprocess, sys

SELF_TEST = os.getenv('SELF_TEST','false').lower()=='true'
DRY = os.getenv('DRY_RUN','false').lower()=='true'

def run_step(cmd):
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)

def main():
    # generation pipeline
    run_step(['python','scripts/generate_text.py'])
    run_step(['python','scripts/generate_images.py','assets/content.json'])
    run_step(['python','scripts/generate_audio.py','assets/content.json','assets/audio.mp3'])
    run_step(['python','scripts/assemble_video.py','assets','assets/video_post.mp4'])
    if SELF_TEST:
        print('[SELF TEST] Validating payloads (no external API calls will be made).')
        # run validators
        run_step(['python','-c','from helpers.validate_payloads import validate_all_payloads; validate_all_payloads()'])
        print('[SELF TEST] Completed successfully.')
        return
    # Publishing (each script will handle its own auth and errors)
    if DRY:
        os.environ['DRY_RUN'] = 'true'
    run_step(['python','scripts/publish_youtube.py','assets/video_post.mp4'])
    run_step(['python','scripts/publish_instagram.py','assets'])
    run_step(['python','scripts/publish_linkedin.py','assets'])
    run_step(['python','scripts/publish_x.py'])
    print('Publish steps completed. Check logs above for details.')

if __name__ == '__main__':
    main()
