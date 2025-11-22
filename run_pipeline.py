import os
import json
import sys
from datetime import datetime

from scripts.content_generator import generate_trending_content
from scripts.image_generator import generate_image
from scripts.video_generator import generate_video
from scripts.publisher_twitter import publish_to_twitter

LOG_FILE = "pipeline_log.txt"


def log(message: str):
    """Append logs to file and print."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    final_message = f"[{timestamp}] {message}"
    print(final_message)
    with open(LOG_FILE, "a") as f:
        f.write(final_message + "\n")


def run_self_test():
    """Run a complete self-test without publishing live."""
    log("====== SELF TEST MODE STARTED ======")

    # Step 1 — Generate content
    log("Generating test content…")
    title, body = generate_trending_content(test_mode=True)
    log(f"Generated Content Title: {title}")

    # Step 2 — Generate image
    log("Generating test image…")
    image_path = generate_image(prompt=title, test_mode=True)
    log(f"Generated test image at: {image_path}")

    # Step 3 — Generate video
    log("Generating test video…")
    video_path = generate_video(caption=title, test_mode=True)
    log(f"Generated test video at: {video_path}")

    # Step 4 — Simulate publish
    log("Simulating publish step (no real posting).")
    simulated_post = {
        "title": title,
        "body": body,
        "image_path": image_path,
        "video_path": video_path
    }
    log("SELF-TEST OUTPUT:\n" + json.dumps(simulated_post, indent=2))

    log("====== SELF TEST MODE COMPLETED SUCCESSFULLY ======")


def run_pipeline():
    """Runs full end-to-end live pipeline."""
    log("====== PIPELINE STARTED ======")

    # Step 1 — Generate content
    log("Generating content…")
    title, body = generate_trending_content()
    log(f"Content generated → {title}")

    # Step 2 — Generate image (HuggingFace Diffusers)
    log("Generating image…")
    image_path = generate_image(prompt=title)
    log(f"Image created: {image_path}")

    # Step 3 — (Optional) Generate video
    log("Generating video…")
    video_path = generate_video(caption=title)
    log(f"Video created: {video_path}")

    # Step 4 — Publish to Twitter
    log("Publishing to Twitter…")
    publish_to_twitter(text=title + "\n\n" + body, media_file=image_path)

    log("====== PIPELINE COMPLETED SUCCESSFULLY ======")


if __name__ == "__main__":
    mode = "run"

    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == "self_test":
        run_self_test()
    else:
        run_pipeline()
