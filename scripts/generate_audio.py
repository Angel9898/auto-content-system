"""scripts/generate_audio.py

Generates audio using HuggingFace TTS endpoint or creates a silent placeholder.
Usage: python scripts/generate_audio.py assets/content.json assets/audio.mp3
"""
import os, sys, json, requests

HF_API_KEY = os.getenv('HF_API_KEY')
TTS_MODEL = os.getenv('HF_TTS_MODEL', 'facebook/tts_transformer')

def hf_tts(text, out_path):
    url = f'https://api-inference.huggingface.co/models/{TTS_MODEL}'
    headers = {'Authorization': f'Bearer {HF_API_KEY}'}
    payload = {'inputs': text}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    with open(out_path, 'wb') as f:
        f.write(r.content)

def main():
    src = sys.argv[1] if len(sys.argv)>1 else 'assets/content.json'
    out = sys.argv[2] if len(sys.argv)>2 else 'assets/audio.mp3'
    if not os.path.exists(src):
        print('Content JSON not found. Run generate_text.py first.')
        return
    with open(src) as f:
        data = json.load(f)
    script = data.get('yt_script','') or data.get('linkedin_post','')
    if not script:
        print('No script text found, creating silent mp3 placeholder.')
        open(out,'wb').write(b'')  # placeholder
        return
    try:
        if HF_API_KEY:
            hf_tts(script, out)
        else:
            raise RuntimeError('No HF key')
    except Exception as e:
        print('TTS failed, creating silent placeholder:', e)
        open(out,'wb').write(b'')

if __name__ == '__main__':
    main()
