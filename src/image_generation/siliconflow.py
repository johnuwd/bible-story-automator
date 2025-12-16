import time
import requests
import json
import edge_tts
from moviepy.editor import *
import random

# --- CONFIGURATION ---
SILICON_FLOW_API_KEY = "sk-ihcxnkepwtwrkqndphmuyuzgpvqypuqzxidfxiuadbsgeqjf"

# --- FLUX 1 PRO GENERATOR FUNCTION ---
def generate_image_flux_pro(prompt):
    """
    Generates an image using the Flux 1 Pro model via SiliconFlow API.
    """
    url = "https://api.siliconflow.com/v1/images/generations"  # Check documentation for exact endpoint

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    # Flux Pro Payload
    # payload = {
    #     "model": "Tongyi-MAI/Z-Image-Turbo", # Ensure this model ID matches SiliconFlow's current listing
    #     "prompt": prompt,
    #     "image_size": "1024x576", # 16:9 Cinematic Aspect Ratio
    #     # "num_inference_steps": 25, # Flux is fast, 20-25 is usually enough
    #     # "guidance_s   cale": 7.5,
    #     # "prompt_upsampling": True,
    #     "seed": 0 # Random seed
    # }
    
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell", 
        "prompt": prompt,
        "image_size": "1024x576", # 16:9 Cinematic
        "num_inference_steps": 4, # Schnell only needs 4 steps! (Very Fast)
        "seed": random.randint(1, 999999999) # Random seed for variety
    }

    print(f"      🎨 Sending to Flux Pro...", end="", flush=True)
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # SiliconFlow usually returns the URL directly in the response
            # Adjust parsing based on exact API response structure
            image_url = data['data'][0]['url'] 
            print(" Done!")
            return image_url
        else:
            print(f" ❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f" ❌ Exception: {e}")
        return None

def download_image(url, save_path):
    try:
        img_data = requests.get(url).content
        with open(save_path, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        print(f"Failed to download image: {e}")

# --- UPDATED ASSETS GENERATOR ---
async def generate_assets_flux(script):
    clips = []
    
    # Flatten script parts (Story + Lesson + Blessing)
    all_scenes = script.get('scenes', [])
    if 'lesson' in script: all_scenes.append(script['lesson'])
    if 'blessing' in script: all_scenes.append(script['blessing'])

    print(f"🎬 Processing {len(all_scenes)} segments using Flux 1 Pro...")

    for i, scene in enumerate(all_scenes):
        print(f"   [Segment {i+1}]")

        # 1. AUDIO (EdgeTTS)
        audio_path = f"audio_{i}.mp3"
        narration = scene.get('narration_telugu', scene.get('narration', '')) 
        communicate = edge_tts.Communicate(narration, "te-IN-ShrutiNeural")
        await communicate.save(audio_path)

        # 2. IMAGE (Flux Pro via SiliconFlow)
        img_path = f"image_{i}.png"
        
        # Enhance prompt for Flux
        # Flux loves natural language, so we don't need too many tag soups like "masterpiece, best quality"
        visual_prompt = f"{scene['visual']}, cinematic lighting, 3D animated movie style, detailed texture, 8k resolution"
        
        final_image_url = generate_image_flux_pro(visual_prompt)
        
        if final_image_url:
            download_image(final_image_url, img_path)
        else:
            print("⚠️ Image generation failed, creating placeholder.")
            # Create black placeholder
            ImageClip(size=(1024, 576), color=(0,0,0)).save_frame(img_path)

        # 3. VIDEO CLIP (Ken Burns Zoom)
        audio_clip = AudioFileClip(audio_path)
        clip = (ImageClip(img_path)
                .set_duration(audio_clip.duration + 0.5)
                .resize(lambda t: 1 + 0.02*t) # Slow Zoom
                .set_position(('center', 'center'))
                .set_audio(audio_clip)
                .set_fps(24))
        
        clips.append(clip)

    return clips

visual = "Young boy, curly brown hair, wearing a vibrant multi-colored striped coat with a golden belt around his waist, and a gentle smile on his face. High angle shot of Joseph being thrown into the well, with a sense of danger and urgency in the scene, and a dramatic music playing in the background. cinematic lighting, 3D animated movie style, pixar style, 8k resolution, masterpiece"
image_url = generate_image_flux_pro(visual)
download_image(image_url, "joseph.png")