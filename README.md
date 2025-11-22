# Zero-cost Auto-Posting System (Full Production Code)

This repository contains a zero-cost, long-term automation pipeline that:
- Generates high-quality content (text via Gemini3Pro / ChatGPT; microtasks via Gemini Nano).
- Generates visuals via HuggingFace SDXL image inference.
- Produces audio via HuggingFace TTS (or 11Labs optionally).
- Assembles vertical shorts / reels via FFmpeg on GitHub Actions runners.
- Publishes to YouTube, Instagram (Business Graph API), LinkedIn, and X (Twitter).
- Includes a SELF_TEST mode to simulate and validate payloads without posting.

**Important:** This code expects you to provide environment secrets in GitHub Actions or as environment variables when running locally. See `secrets.example.md` for the full list.

## Quickstart (test using SELF_TEST)
1. Create a GitHub repo and copy these files.
2. Add secrets per `secrets.example.md` (you can set `SELF_TEST=true` to skip real publishes).
3. In GitHub Actions, run the `daily-content` workflow manually (Actions → Workflows → daily-content → Run workflow).
4. Inspect logs. If SELF_TEST is enabled the run will complete without posting.

## Contents
- scripts/: generation, assembly, and publish scripts
- helpers/: model clients and validators
- templates/: prompts for the models
- .github/workflows/daily.yml: GitHub Actions workflow

**DISCLAIMER:** The publish scripts include safe fallbacks and are heavily commented. They will not work until you add valid API credentials as GitHub secrets or environment variables. For privacy, do not commit secrets to this repo.
