"""scripts/generate_images.py

Generates images for IG carousel and a thumbnail using HuggingFace SDXL inference endpoint.
If HF is not configured or fails, falls back to simple Pillow slides.
Usage: python scripts/generate_images.py assets/content.json
"""
import os, sys, json, requests
from PIL import Image, ImageDraw, ImageFont

HF_API_KEY = os.getenv('HF_API_KEY')
HF_MODEL = os.getenv('HF_IMAGE_MODEL', 'stabilityai/stable-diffusion-xl-base-1.0')

def simple_slide(text, out_path, size=(1080,1350)):
    im = Image.new('RGB', size, (250,250,250))
    d = ImageDraw.Draw(im)
    try:
        font = ImageFont.load_default()
        d.text((60,60), text, fill=(20,20,20), font=font)
    except Exception:
        d.text((60,60), text, fill=(20,20,20))
    im.save(out_path)

def hf_generate_image(prompt, out_path):
    url = f'https://api-inference.huggingface.co/models/{HF_MODEL}'
    headers = {'Authorization': f'Bearer {HF_API_KEY}'}
    payload = {'inputs': prompt}
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    # HF sometimes returns image bytes directly
    with open(out_path, 'wb') as f:
        f.write(r.content)

def main():
    src = sys.argv[1] if len(sys.argv)>1 else 'assets/content.json'
    if not os.path.exists(src):
        print('Content JSON not found. Run generate_text.py first.')
        return
    with open(src) as f:
        data = json.load(f)
    os.makedirs('assets/images', exist_ok=True)
    carousel = data.get('ig_carousel', [])
    title = data.get('title','')
    for i, slide_text in enumerate(carousel, start=1):
        out_path = f'assets/images/slide{i:02d}.png'
        prompt = f"A clean modern social media slide, minimal design, bold typography. Title: {title}. Text: {slide_text}. 1080x1350, high contrast, professional."
        try:
            if HF_API_KEY:
                print('Requesting HF image for slide', i)
                hf_generate_image(prompt, out_path)
            else:
                raise RuntimeError('No HF key')
        except Exception as e:
            print('HF image generation failed, falling back to simple slide:', e)
            simple_slide(slide_text, out_path)
    # thumbnail
    thumb_path = 'assets/thumbnail.png'
    try:
        prompt = f'YouTube thumbnail: {title}. Bold professional layout, readable text, 1280x720'
        if HF_API_KEY:
            hf_generate_image(prompt, thumb_path)
        else:
            raise RuntimeError('No HF key')
    except Exception as e:
        print('Thumbnail HF failed, creating fallback thumbnail:', e)
        simple_slide(title, thumb_path, size=(1280,720))
    print('Image generation complete.')

if __name__ == "__main__":
    main()
