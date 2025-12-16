import os
import json
import random
import requests
from moviepy.editor import *
from dotenv import load_dotenv
import re
from src.utils.rest_api import RestAPI

load_dotenv()

# ==========================================
# ⚙️ CONFIGURATION (FILL THESE KEYS)
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")

LANGUAGE_PROFILE_CACHE = {}


# ==========================================
# 2. STORY GENERATOR (GROQ / LLAMA-3)
# ==========================================
def generate_story_script(topic, AUDIO_LANGUAGE):
    """
    audio_languages: list[str]  -> ["english", "telugu", "hindi"]
    """
    languages_text = ", ".join(AUDIO_LANGUAGE)
    print(f"🧠 Generating {AUDIO_LANGUAGE} Masterpiece Script using DeepSeek-V3 for: {topic}...")
    
    # ⚠️ Check endpoint: SiliconFlow sometimes uses .cn or .com. 
    # If .com fails, try "https://api.siliconflow.com/v1/chat/completions"
    url = "https://api.siliconflow.com/v1/chat/completions"
    
    # 🎬 The "DeepSeek" Prompt (English Version)
    system_prompt = f"""
        You are a Biblical Storyboard Generator for animated Bible stories.

        Your task is to generate a visually consistent, emotionally rich,
        and Biblically accurate script for the story: "{topic}".
        
        ====================
        LANGUAGE REQUIREMENT
        ====================
        - Generate narration in the following languages: {languages_text}
        - Each scene MUST include narration for ALL requested languages.
        - Maintain identical meaning and emotional tone across languages.
        - Language should be simple and suitable for children.
        
        ====================
        STORY OPENING RULE (MANDATORY)
        ====================
        - The FIRST scene must gently set the background of the story.
        - It must:
        • establish time ("Long ago", "In the days of Israel’s kings")
        • establish place ("the land of Israel", "a quiet valley")
        • establish emotion (fear, waiting, hope)
        - Do NOT start with action or conflict in the first scene.
        - The opening should feel like a storyteller inviting the listener in.

        ====================
        BIBLICAL GUARDBANDS
        ====================
        - Do NOT add events that contradict the Bible.
        - Expanded dialogue is allowed ONLY to express emotion, not new facts.
        - Maintain reverence, hope, and moral clarity.
        - Language must be suitable for children.

        ====================
        SCENE GENERATION RULES
        ====================
        - Create a NEW scene whenever:
        • the visual setting changes
        • a new character becomes the focus
        • the emotional tone shifts
        • an important action occurs
        - Each scene narration should feel like ~5–8 seconds when read aloud.
        - If narration feels long, SPLIT into multiple scenes.

        ====================
        CHARACTER CONSISTENCY
        ====================
        - Define all important characters once as anchors.
        - NEVER repeat physical descriptions inside scenes.
        - Scenes must reference actions, not appearances.

        ====================
        NARRATION STYLE
        ====================
        - Warm, emotional, storyteller voice (grandparent tone).
        - 3–4 natural sentences per scene.
        - Include gentle dialogue where appropriate.

        ====================
        VISUAL DIRECTION
        ====================
        - Describe camera angle, mood, and action.
        - The visual must depict the EXACT narrated moment.
        - Do NOT restate character descriptions.

        ====================
        OUTPUT FORMAT (JSON ONLY)
        ====================
        {{
        "character_anchors": {{
            "CharacterName": "Concise visual identity"
        }},
        "scenes": [
            {{
            "narration": {{
                "en": "...",
                "te": "..."
            }},
            "visual_action": "Cinematic visual description"
            }}
        ],
        "lesson": {{
            "narration": {{
            "en": "...",
            "te": "..."
            }},
            "visual_action": "Symbolic peaceful image"
        }},
        "blessing": {{
            "narration": {{
            "en": "...",
            "te": "..."
            }},
            "visual_action": "Calm hopeful image"
        }}
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
        # response = requests.post(url, json=payload, headers=headers)
        response = RestAPI.request(url=url, method="POST", headers=headers, payload=payload, timeout=180)
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


def generate_video_metadata(topic, story_script_data=None, language="english"):
    """
    Generates YouTube Title, Description, Tags, and Category ID
    in the requested language.
    """
    lang_cfg = get_cached_language_profile(language)
    
    url = "https://api.siliconflow.com/v1/chat/completions"

    # ---------- Context ----------
    context = f"Story Topic: {topic}"

    if story_script_data and "scenes" in story_script_data:
        preview_lines = []
        for scene in story_script_data["scenes"][:2]:
            narration = scene.get("narration", {}).get(language)
            if narration:
                preview_lines.append(narration)

        if preview_lines:
            context += "\nStory Preview: " + " ".join(preview_lines)

    # ---------- System Prompt ----------
    system_prompt = f"""
        You are a YouTube Growth Strategist & SEO Expert.

        TARGET LANGUAGE:
        - Language: {lang_cfg["language_name"]}
        - Audience: {lang_cfg["audience"]}

        GOAL:
        Generate high-performing YouTube metadata for a Bible story video.

        STRICT RULES:
        1. Title, Description, and Tags MUST be written ONLY in {lang_cfg["language_name"]}.
        2. Language must sound natural and native (not translated word-by-word).
        3. Content must be suitable for children and families.
        4. Optimize for emotional curiosity and faith-based discovery.

        TITLE RULES:
        - Under 100 characters
        - Emotional, curious, or faith-driven
        - Must include the story topic
        - Must include the phrase "{lang_cfg['bible_phrase']}"

        DESCRIPTION RULES:
        - 3–4 short sentences
        - Summarize the story emotionally
        - End with this call-to-action (translated naturally):
        "{lang_cfg['cta']}"
        - Include 5–10 relevant hashtags in {lang_cfg["language_name"]}

        TAGS RULES:
        - 15–20 high-search keywords
        - {lang_cfg["tags_hint"]}
        - May include English keywords ONLY if commonly searched in YouTube India

        CATEGORY:
        Choose the ONE best category:
        - 1 = Film & Animation
        - 22 = People & Blogs
        - 27 = Education

        OUTPUT FORMAT (STRICT JSON ONLY):
        {{
        "title": "...",
        "description": "...",
        "tags": ["...", "..."],
        "category_id": "1"
        }}
        """

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # response = requests.post(url, json=payload, headers=headers)
        response = RestAPI.request(url=url, method="POST", headers=headers, payload=payload, timeout=180)
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```", "", content)

        return json.loads(content)

    except Exception as e:
        print(f"❌ Metadata Generation Error [{language}]: {e}")
        return None
    

def get_language_profile(language_code):
    """
    Dynamically generates language-specific YouTube metadata preferences.
    Cache the result per language.
    """
    url = "https://api.siliconflow.com/v1/chat/completions"

    system_prompt = f"""
        You are a multilingual YouTube SEO expert.

        TASK:
        Given a language code, generate culturally appropriate metadata hints
        for Bible story videos on YouTube.

        RULES:
        - Use native language text wherever appropriate
        - Keep content suitable for Christian family audiences in India
        - Be concise and practical

        OUTPUT STRICT JSON:
        {{
        "language_name": "...",
        "audience": "...",
        "bible_phrase": "...",
        "cta": "...",
        "tags_hint": "..."
        }}
        """

    payload = {
        "model": "deepseek-ai/DeepSeek-V3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Language code: {language_code}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.4,
        "max_tokens": 512
    }

    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # response = requests.post(url, json=payload, headers=headers)
        response = RestAPI.request(url=url, method="POST", headers=headers, payload=payload, timeout=180)
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        content = re.sub(r"```json\s*", "", content)
        content = re.sub(r"```", "", content)

        return json.loads(content)

    except Exception as e:
        print(f"❌ Language profile generation failed: {e}")

        # 🔒 SAFE FALLBACK
        return {
            "language_name": language_code.upper(),
            "audience": f"{language_code} speaking Christian audience",
            "bible_phrase": "Bible Story",
            "cta": "Subscribe for more Bible Stories!",
            "tags_hint": "Bible and Christian keywords"
        }


def get_cached_language_profile(language_code):
    if language_code not in LANGUAGE_PROFILE_CACHE:
        LANGUAGE_PROFILE_CACHE[language_code] = get_language_profile(language_code)
    return LANGUAGE_PROFILE_CACHE[language_code]