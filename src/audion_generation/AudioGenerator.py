import os
import requests
import json
import re
import edge_tts
import asyncio
from src.utils.rest_api import RestAPI
from dotenv import load_dotenv

load_dotenv()
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")

class AudioGenerator:
    
    VOICE_PROFILE_CACHE = {}

    # ======================================================
    # 🔹 EXISTING LOGIC (FOR ENGLISH / FISH AUDIO)
    # ======================================================
    @staticmethod
    def get_voice_profile(language_code):
        if language_code in AudioGenerator.VOICE_PROFILE_CACHE:
            return AudioGenerator.VOICE_PROFILE_CACHE[language_code]

        # Simplified for English-only focus in this section
        fallback = {
            "voice": "fishaudio/fish-speech-1.5:benjamin", 
            "speed": 1.0
        }
        return fallback

    @staticmethod
    def _generate_english_fish(text, output_path):
        """Your existing code for high-quality English narration"""
        print(f"   🎙️ Generating English Audio (Fish Audio)...", end="", flush=True)
        
        voice_profile = AudioGenerator.get_voice_profile("en")
        url = "https://api.siliconflow.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "fishaudio/fish-speech-1.5",
            "input": text,
            "voice": voice_profile["voice"],
            "response_format": "mp3",
            "sample_rate": 32000,
            "stream": False,
            "speed": voice_profile["speed"],
            "gain": 0.0
        }

        try:
            # response = requests.post(url, json=payload, headers=headers, timeout=180)
            response = RestAPI.request(url=url, method="POST", headers=headers, payload=payload, timeout=180)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(" Done!")
                return True
            else:
                print(f" ❌ API Error: {response.text}")
                return False
        except Exception as e:
            print(f" ❌ Exception: {e}")
            return False

    # ======================================================
    # 🔹 NEW LOGIC (FOR TELUGU/HINDI / EDGE TTS)
    # ======================================================
    @staticmethod
    def _translate_text(text, target_lang):
        """Translates English text to Target Language using DeepSeek"""
        print(f"   🔄 Translating to {target_lang}...", end="", flush=True)
        
        url = "https://api.siliconflow.com/v1/chat/completions"
        system_prompt = f"Translate the following text to {target_lang}. Output ONLY the translated text. No notes."
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
            "temperature": 0.3,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {SILICON_FLOW_API_KEY}", "Content-Type": "application/json"})
            return response.json()['choices'][0]['message']['content'].strip()
        except:
            return text # Fallback to original text

    @staticmethod
    async def _generate_other_edge(text, output_path, language):
        """Uses Edge TTS for native Indian language support"""
        
        # 1. Translate Text First!
        translated_text = AudioGenerator._translate_text(text, language)
        
        # 2. Select Voice
        voices = {
            "te": "te-IN-MohanNeural",       # Telugu
            "hi": "hi-IN-MadhurNeural",      # Hindi
            "ta": "ta-IN-ValluvarNeural",    # Tamil
            "ml": "ml-IN-MidhunNeural"       # Malayalam
        }
        voice = voices.get(language, "te-IN-MohanNeural")
        
        print(f"   🎙️ Generating {language} Audio (Edge TTS)...", end="", flush=True)
        try:
            communicate = edge_tts.Communicate(translated_text, voice)
            await communicate.save(output_path)
            print(" Done!")
            return True
        except Exception as e:
            print(f" ❌ EdgeTTS Error: {e}")
            return False

    # ======================================================
    # 🔹 UNIFIED ENTRY POINT
    # ======================================================
    @staticmethod
    async def generate(text, output_path, language="en"):
        """
        Main function to call from your script.
        - If English: Uses your original Fish Audio code.
        - If Other: Uses Edge TTS (Async).
        """
        if language == "en":
            # Call the synchronous Fish Audio function
            return AudioGenerator._generate_english_fish(text, output_path)
        else:
            # Call the async Edge TTS function
            return await AudioGenerator._generate_other_edge(text, output_path, language)