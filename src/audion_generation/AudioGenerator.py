import os
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# ⚙️ CONFIGURATION (FILL THESE KEYS)
# ==========================================
SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")

    
def generate_english_audio(text, output_path):
    print(f"🎙️ Generating English Audio for: {text[:30]}...")
    
    url = "https://api.siliconflow.com/v1/audio/speech"
    
    headers = {
        "Authorization": f"Bearer {SILICON_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "fishaudio/fish-speech-1.5",
        "input": text,
        
        # 🎤 VOICE SELECTION:
        # "fishaudio/fish-speech-1.5:benjamin" -> Deep, storytelling male (Best for this)
        # "fishaudio/fish-speech-1.5:alex"     -> Standard male
        # "fishaudio/fish-speech-1.5:anna"     -> Standard female
        "voice": "fishaudio/fish-speech-1.5:benjamin", 
        
        "response_format": "mp3",
        "sample_rate": 32000,
        "stream": True,
        "speed": 1.0,
        "gain": 0.0
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print("   ✅ Audio saved!")
            return True
        else:
            print(f"   ❌ TTS Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
