import os
import json
import random
import requests
from moviepy.editor import *
from dotenv import load_dotenv
import re

load_dotenv()

# ==========================================
# ⚙️ CONFIGURATION (FILL THESE KEYS)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")

# ==========================================
# 2. STORY GENERATOR (GROQ / LLAMA-3)
# ==========================================
def generate_story_script(topic):
    print(f"🧠 Generating English Masterpiece Script using DeepSeek-V3 for: {topic}...")
    
    # ⚠️ Check endpoint: SiliconFlow sometimes uses .cn or .com. 
    # If .com fails, try "https://api.siliconflow.com/v1/chat/completions"
    url = "https://api.siliconflow.com/v1/chat/completions"
    
    # 🎬 The "DeepSeek" Prompt (English Version)
    system_prompt = f"""
    You are an expert AI Movie Director and a Warm English Storyteller (Grandpa style).
    
    ### GOAL
    Create a highly engaging, emotional, and visually consistent script for a children's animation about "{topic}".
    
    ### SCENE RULES (How to decide when to make a new scene):
    1. **Visual Shifts:** Create a NEW scene whenever the visual needs to change (e.g., character moves, new person enters, mood shifts from happy to sad).
    2. **Pacing:** Never let a single scene's narration go longer than 3 sentences. If the text is long, split it into two scenes with slightly different visuals (e.g., Wide Shot -> Close Up).
    3. **Completeness:** Ensure the story has a clear Beginning, Middle, and End.

    ### ROLE 1: The English Storyteller (Narration)
    - **Tone:** Warm, deep, emotional, and captivating. Think "Disney Movie Narrator".
    - **Language:** Simple but evocative English suitable for kids and adults.
    - **Structure:**
        - **Hooks:** Start scenes with engaging phrases: "But suddenly...", "Do you know what happened next?", "Alas...".
        - **Length:** Each narration MUST be 3-4 sentences. Avoid short, dry summaries.
        - **Dialogue:** Include characters speaking! "Joseph cried out, 'Please, brothers, do not do this!'"
    
    ### ROLE 2: The Visual Director (Image Prompts)
    - **CRITICAL RULE:** Do not use abstract words like "brave", "sad", or "faithful".
    - **INSTEAD:** Describe physical actions. 
      - Bad: "David looks brave."
      - Good: "Low angle shot of David holding a sling, eyebrows frowned, looking up at the sky."
    - **Structure:** Start EVERY visual_action with the camera angle (e.g., "Wide shot of...", "Close up of...").
    - **Sync:** The visual MUST depict the *exact moment* described in the narration.

    ### OUTPUT FORMAT (Strict JSON only, no markdown):
    {{
      "character_anchor": "A young Middle-Eastern boy, curly brown hair, wearing a vibrant multi-colored patchwork coat of many colors",
      "scenes": [
        {{ 
            "narration_english": "Detailed emotional English narration...", 
            "visual_action": "Wide cinematic shot of [Action], dramatic lighting, 8k..."
        }}
      ],
      "lesson": {{ "narration_english": "...", "visual_action": "Symbolic image..." }},
      "blessing": {{ "narration_english": "...", "visual_action": "Peaceful image..." }}
    }}
    """

    payload = {
        "model": "deepseek-ai/DeepSeek-V3", # 🏆 Best for Logic + Creative Writing
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write the script for: {topic}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 1.1, # High creativity for better storytelling
        "max_tokens": 4096
    }

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Check for HTTP errors
        
        # Parse JSON
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        
        # 🛡️ Safety Clean: Remove Markdown code blocks if DeepSeek adds them
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```', '', content)
        
        return json.loads(content)

    except Exception as e:
        print(f"❌ Story Generation Error: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return None


# ==========================================
# 3. IMAGE GENERATOR (SILICON FLOW / FLUX SCHNELL)
# ==========================================
def generate_image_flux(prompt, save_path):
    url = "https://api.siliconflow.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "black-forest-labs/FLUX.1-schnell", # Fast & Good Animation Style
        "prompt": prompt,
        "image_size": "1024x576",
        "num_inference_steps": 4,
        "seed": random.randint(1, 999999999)
    }

    print(f"   🎨 Generating Image...", end="", flush=True)
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            image_url = response.json()['data'][0]['url']
            
            # Download immediately
            img_data = requests.get(image_url).content
            with open(save_path, 'wb') as handler:
                handler.write(img_data)
            print(" Done!")
            return True
        else:
            print(f" ❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f" ❌ Exception: {e}")
        return False
    
def generate_video_metadata(topic, story_script_data=None):
    """
    Generates YouTube Title, Description, Tags, and Category ID using DeepSeek-V3.
    """
    print(f"📈 Generating YouTube Metadata for: {topic}...")

    url = "https://api.siliconflow.com/v1/chat/completions"

    # Context for the AI: Give it a summary if available, otherwise just use the topic
    context = f"Topic: {topic}"
    if story_script_data and "scenes" in story_script_data:
        # Grab the first 2 narrations to give the AI a taste of the story
        preview = " ".join([s.get("narration_english", "") for s in story_script_data["scenes"][:2]])
        context += f"\nStory Preview: {preview}"

    system_prompt = """
    You are a YouTube Growth Strategist & SEO Expert specializing in Christian/Bible content for Indian audiences (English speaking).
    
    ### GOAL
    Generate high-viral potential metadata for a YouTube Short/Video about a Bible story.
    
    ### REQUIREMENTS
    1. **Title:** - Must be catchy, emotional, or mysterious. 
       - MUST include "Telugu Bible Story" and the Topic Name.
       - Under 100 characters.
       - Example: "God's Amazing Plan! Joseph's Story - English Bible Story (AI Animation)"
    
    2. **Description:**
       - 3-4 sentences summarizing the story passionately.
       - Include a call to action: "Subscribe for more Bible Stories!"
       - Include 5-10 strong hashtags.
    
    3. **Tags:**
       - A list of 15-20 high-volume search keywords (mixed English and Telugu transliteration).
       - Examples: "Bible stories", "Jesus", "Devotional", "Sunday School", "Telugu Christian".

    4. **Category ID:**
       - Choose the best YouTube Category ID. 
       - '22' (People & Blogs) is standard for vlogs/stories.
       - '1' (Film & Animation) is good for AI animations.
       - '27' (Education) is good for moral stories.
       - Pick the one that maximizes reach.

    ### OUTPUT FORMAT (Strict JSON only):
    {
       "title": "...",
       "description": "...",
       "tags": ["tag1", "tag2", ...],
       "category_id": "22"
    }
    """

    payload = {
        "model": "deepseek-ai/DeepSeek-V3", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate metadata for: {context}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7, # Slightly lower temp for precise SEO data
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        content = response.json()['choices'][0]['message']['content']
        
        # Safety Clean: Remove Markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```', '', content)
        
        return json.loads(content)

    except Exception as e:
        print(f"❌ Metadata Generation Error: {e}")
        return None