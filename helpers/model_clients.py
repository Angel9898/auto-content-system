"""helpers/model_clients.py

Abstraction layer for model APIs:
- gen_text_gemini(prompt): primary generator using Gemini 3 Pro (or fallback)
- rewrite_with_chatgpt(text): optional rewriter using ChatGPT/OpenAI-compatible endpoint
- microtask_with_nano(task, text): fast microtasks using Nano endpoint or heuristics

This file uses environment variables for keys. It does not embed keys.
"""
import os
import requests
import json
from typing import Optional

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_ENDPOINT = os.getenv('GEMINI_ENDPOINT')  # optional custom endpoint
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')
OPENAI_API_URL = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions')
HF_API_KEY = os.getenv('HF_API_KEY')

def gen_text_gemini(prompt: str, max_tokens: int = 800) -> str:
    """Generate text using Gemini 3 Pro via the Google Generative API.
    Falls back to a HuggingFace text model if Gemini is not configured.
    Returns the raw string output from the model.
    """
    if GEMINI_API_KEY and GEMINI_ENDPOINT:
        headers = {'Authorization': f'Bearer {GEMINI_API_KEY}', 'Content-Type': 'application/json'}
        payload = {'prompt': prompt, 'max_output_tokens': max_tokens}
        try:
            resp = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Expecting a structure with 'candidates' or similar; adapt to your endpoint
            if 'candidates' in data and isinstance(data['candidates'], list):
                return data['candidates'][0].get('content','')
            return data.get('output_text') or json.dumps(data)
        except Exception as e:
            print('Gemini call failed:', e)
    # Fallback: HuggingFace (lightweight)
    if HF_API_KEY:
        hf_model = os.getenv('HF_TEXT_MODEL','gpt2')
        hf_url = f'https://api-inference.huggingface.co/models/{hf_model}'
        headers = {'Authorization': f'Bearer {HF_API_KEY}'}
        try:
            r = requests.post(hf_url, headers=headers, json={'inputs': prompt}, timeout=60)
            r.raise_for_status()
            res = r.json()
            if isinstance(res, list) and len(res)>0:
                return res[0].get('generated_text','')
            return res.get('generated_text','') if isinstance(res, dict) else str(res)
        except Exception as e:
            print('HF text fallback failed:', e)
    raise RuntimeError('No text model configured (set GEMINI_API_KEY+GEMINI_ENDPOINT or HF_API_KEY)')

def rewrite_with_chatgpt(text: str, instruction: Optional[str]=None) -> str:
    """Rewrite the provided text using ChatGPT/OpenAI-like API.
    If CHATGPT_API_KEY is not provided, returns the original text.
    """
    if not CHATGPT_API_KEY:
        return text
    system_msg = instruction or 'Rewrite to be concise, professional, and engaging.'
    payload = {
        'model': 'gpt-4o-mini',
        'messages': [
            {'role':'system','content': system_msg},
            {'role':'user','content': text}
        ],
        'max_tokens': 400
    }
    headers = {'Authorization': f'Bearer {CHATGPT_API_KEY}', 'Content-Type': 'application/json'}
    try:
        r = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        return j['choices'][0]['message']['content']
    except Exception as e:
        print('ChatGPT rewrite failed:', e)
        return text

def microtask_with_nano(task: str, text: str):
    """Perform small microtasks with a Nano endpoint. Falls back to local heuristics.
    Supported tasks: 'hashtags', 'titles', 'keywords'
    """
    nano_url = os.getenv('GEMINI_NANO_ENDPOINT')
    nano_key = os.getenv('GEMINI_NANO_KEY')
    if nano_url and nano_key:
        try:
            r = requests.post(nano_url, headers={'Authorization':f'Bearer {nano_key}'}, json={'task':task,'text':text}, timeout=10)
            r.raise_for_status()
            return r.json().get('result')
        except Exception as e:
            print('Nano call failed:', e)
    # fallback heuristics
    if task == 'hashtags':
        words = [w.strip('.,!?#').lower() for w in text.split() if len(w)>4]
        tags = []
        for w in words:
            tag = '#'+''.join(ch for ch in w if ch.isalnum())
            if tag not in tags:
                tags.append(tag)
            if len(tags) >= 5:
                break
        return tags
    if task == 'titles':
        # return first 8-word slices as variations
        parts = text.split()
        variations = []
        for i in range(min(8, len(parts))):
            variations.append(' '.join(parts[:i+1]))
        return variations
    if task == 'keywords':
        return list(dict.fromkeys([w.strip('.,').lower() for w in text.split() if len(w)>5]) )[:8]
    return None
