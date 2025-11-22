"""scripts/generate_text.py

Generates content.json using the multi-model pipeline:
1. Gemini 3 Pro for primary generation (via helpers.model_clients.gen_text_gemini)
2. ChatGPT for rewriting/humanizing (helpers.model_clients.rewrite_with_chatgpt)
3. Gemini Nano for microtasks (helpers.model_clients.microtask_with_nano)

Output: assets/content.json
"""
import os, json
from helpers.model_clients import gen_text_gemini, rewrite_with_chatgpt, microtask_with_nano

os.makedirs('assets', exist_ok=True)

PROMPT_TEMPLATE = open('templates/prompt_templates.md').read()

def build_production_prompt():
    # Simplified: in production you may add trending signals
    return PROMPT_TEMPLATE + "\nTopic: AI productivity hacks.\nProvide JSON as specified."

def main():
    prompt = build_production_prompt()
    print('Generating primary content (Gemini)...')
    raw = gen_text_gemini(prompt)
    # Try to parse JSON output; if not valid, ask rewrite_with_chatgpt to structure it
    try:
        data = json.loads(raw)
    except Exception:
        print('Primary output not valid JSON, attempting to restructure via ChatGPT...')
        structured = rewrite_with_chatgpt(raw, instruction='Return a JSON object with keys: title, linkedin_post, x_post, ig_carousel (list), yt_script, hashtags')
        try:
            data = json.loads(structured)
        except Exception:
            print('Restructure failed — using heuristic extraction.')
            data = {
                'title': (raw.split('\n')[0] if raw else 'AI Productivity'),
                'linkedin_post': raw[:2000],
                'x_post': raw[:280],
                'ig_carousel': [raw[i:i+120] for i in range(0,600,120)][:5],
                'yt_script': raw[:800],
                'hashtags': microtask_with_nano('hashtags', raw)
            }
    # Post-process with ChatGPT for tone and virality
    print('Rewriting for tone with ChatGPT...')
    data['linkedin_post'] = rewrite_with_chatgpt(data.get('linkedin_post',''), 'Rewrite to be professional, concise, and include 3 actionable tips. Max 300 words.')
    data['x_post'] = rewrite_with_chatgpt(data.get('x_post',''), 'Make this a punchy 280-char post with 2 hashtags.')
    # microtasks
    data['hashtags'] = microtask_with_nano('hashtags', data.get('linkedin_post',''))
    # Save output
    with open('assets/content.json','w') as f:
        json.dump(data, f, indent=2)
    print('Wrote assets/content.json')

if __name__ == '__main__':
    main()
