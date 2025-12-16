import asyncio
import json
import random

from moviepy.editor import *
from dotenv import load_dotenv
from src.youtube_uploader import upload
from src.story_generator import StoryGenerator
from src.audion_generation.AudioGenerator import AudioGenerator
from src.image_generation import ImageGenerator
from src.utils import Utils


load_dotenv()

# ==========================================
# ⚙️ CONFIGURATION (FILL THESE KEYS)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")
# Topic of the story
TOPIC = "story of job from the bible"
AUDIO_LANGUAGE = ["en"]  # Options: "english", "telugu"
# ==========================================
# 1. SETUP FOLDERS
# ==========================================
def setup_folders(topic_name):
    # Clean up topic name for folder safety (Joseph's Coat -> Josephs_Coat)
    safe_name = topic_name.replace(" ", "_").replace("'", "")
    
    base_dir = os.path.join("Output", safe_name)
    img_dir = os.path.join(base_dir, "images")
    aud_dir = os.path.join(base_dir, "audio")
    
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(aud_dir, exist_ok=True)
    
    for language in AUDIO_LANGUAGE:
        lang_aud_dir = os.path.join(aud_dir, language)
        os.makedirs(lang_aud_dir, exist_ok=True)
    
    print(f"📂 Created folders at: {base_dir}")
    return base_dir, img_dir, aud_dir


# ==========================================
# 4. MAIN PIPELINE (The Glue)
# ==========================================
async def main():
    base_dir, img_dir, aud_dir = setup_folders(TOPIC)
    
    # --- 1. Get Script ---
    script = StoryGenerator.generate_story_script(TOPIC, AUDIO_LANGUAGE)
    print(f"Script: {script}")
    
      
    # 🛑 CRITICAL CHECK: Stop if script is None
    if not script:
        print("❌ Script generation failed. Exiting.")
        return

    # Flatten script
    all_segments = script['scenes'] + [script['lesson']] + [script['blessing']]
    anchor = script.get('character_anchor', "Biblical character, 3d animation style")
    story_seed = random.randint(1, 999999)
    
    
    print(f"🚀 Starting Production: {len(all_segments)} Segments")
    video_clips = []

    for language in AUDIO_LANGUAGE:   
        for i, segment in enumerate(all_segments):
            print(f"\n[Segment {i+1}]")
            
            # --- A. Audio Generation ---
            audio_path = os.path.join(aud_dir, language, f"audio_{i}.mp3")
            # 🔑 FIXED: Use 'narration_english' key
            text = segment.get('narration', "Error in script text.").get(language, "Language not available.")
            await AudioGenerator.generate(text, audio_path, language)
    
    

    for i, segment in enumerate(all_segments):
        # --- B. Image Generation ---
        img_path = os.path.join(img_dir, f"image_{i}.png")
        action = segment.get('visual_action', "Cinematic scene")
        
        final_prompt = (
            f"{action}. "
            f"Subject is {anchor}. "
            "Style: Hand-drawn 2D animation, cel shaded, epic cinematic lighting, "
            "matte painting background, 4k resolution, masterpiece, intricate details. "
            "NO 3D, NO photorealism."
        )
        
        success = ImageGenerator.generate_image_flux(final_prompt, img_path, seed=story_seed)
        
        if not success:
            # Create black placeholder if API fails
            ColorClip(size=(1024, 576), color=(0,0,0)).save_frame(img_path)

        
    
    for language in AUDIO_LANGUAGE:
        video_clips = []
        for i, segment in enumerate(all_segments):
            audio_path = os.path.join(aud_dir, language, f"audio_{i}.mp3")
            img_path = os.path.join(img_dir, f"image_{i}.png")
            # --- C. Combine into Video Clip ---
            image_clip = Utils.video_clip_generation(audio_path, img_path)
            video_clips.append(image_clip)
               
        # assemble the final video after all segments
        output_path = Utils.assemble_video(video_clips, base_dir, language)

        # --- 4. Upload to YouTube ---
        meta_data = StoryGenerator.generate_video_metadata(TOPIC, script, language)
        print(f"📝 Video Metadata: {meta_data}")
        with open(os.path.join(aud_dir,language,"meta_data_debug.txt"), "w", encoding="utf-8") as f:
            json.dump(meta_data, f,indent=4)
            
        upload.upload_video_to_youtube(output_path, meta_data)
        
    

if __name__ == "__main__":
    asyncio.run(main())