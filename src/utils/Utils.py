import os
from moviepy.editor import *

import PIL.Image

# 🩹 MONKEY PATCH: Fix for MoviePy 1.0.3 with new Pillow versions
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS


def video_clip_generation(audio_path, img_path):
    # --- C. Video Clip Creation ---
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration + 0.5
        except:
            print("   ⚠️ Audio load failed, using silent fallback.")
            duration = 5
            audio_clip = None

        image_clip = (ImageClip(img_path)
                      .set_duration(duration)
                      .resize(lambda t: 1 + 0.02*t) # Slow Zoom
                      .set_position(('center', 'center'))
                      .set_fps(24))
        
        if audio_clip:
            image_clip = image_clip.set_audio(audio_clip)
        
        return image_clip

def assemble_video(video_clips, base_dir, language):
        # --- 3. Final Assembly ---
    print("\n📼 Assembling Final Video...")
    if video_clips:
        final_video = concatenate_videoclips(video_clips, method="compose")
        output_video_path = os.path.join(base_dir, f"Final_Video_{language}.mp4")
        
        # Added audio_codec="aac" for better compatibility
        final_video.write_videofile(output_video_path, fps=24, codec="libx264", audio_codec="aac")
        print(f"\n✅ SUCCESS! Video saved at: {output_video_path}")
        
        return output_video_path