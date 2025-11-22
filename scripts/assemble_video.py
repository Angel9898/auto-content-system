"""scripts/assemble_video.py

Assembles slides and audio into a vertical MP4 using ffmpeg CLI calls.
Usage: python scripts/assemble_video.py assets assets/video_post.mp4
"""
import os, sys, subprocess

def make_inputs_txt(image_files, txt_path, per_slide_duration=3):
    with open(txt_path,'w') as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {per_slide_duration}\n")
        # repeat last frame to hold
        f.write(f"file '{image_files[-1]}'\n")

def main():
    assets = sys.argv[1] if len(sys.argv)>1 else 'assets'
    out = sys.argv[2] if len(sys.argv)>2 else os.path.join(assets,'video_post.mp4')
    images_dir = os.path.join(assets,'images')
    if not os.path.exists(images_dir):
        print('No images found; run generate_images.py first.')
        return
    images = sorted([os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith('.png') or f.endswith('.jpg')])
    if not images:
        print('No images to assemble.')
        return
    tmp_list = os.path.join(assets,'inputs.txt')
    make_inputs_txt(images, tmp_list)
    tmp_vid = os.path.join(assets,'temp_slideshow.mp4')
    # slideshow
    cmd1 = ['ffmpeg','-y','-f','concat','-safe','0','-i',tmp_list,'-vf','scale=1080:1920,format=yuv420p','-r','30',tmp_vid]
    print('Running:', ' '.join(cmd1))
    subprocess.check_call(cmd1)
    # combine with audio if present
    audio = os.path.join(assets,'audio.mp3')
    if os.path.exists(audio) and os.path.getsize(audio) > 0:
        cmd2 = ['ffmpeg','-y','-i',tmp_vid,'-i',audio,'-c:v','libx264','-c:a','aac','-shortest',out]
    else:
        cmd2 = ['ffmpeg','-y','-i',tmp_vid,'-c:v','libx264','-an',out]
    print('Running:', ' '.join(cmd2))
    subprocess.check_call(cmd2)
    print('Video assembled at', out)

if __name__ == '__main__':
    main()
