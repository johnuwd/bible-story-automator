import requests
from dotenv import load_dotenv
import os
import random

load_dotenv()

SILICON_FLOW_API_KEY = os.getenv("SILICON_FLOW_API_KEY")


# ==========================================
# 3. IMAGE GENERATOR (SILICON FLOW / FLUX SCHNELL)
# ==========================================
def generate_image_flux(prompt, save_path, seed):
    final_seed = seed if seed is not None else random.randint(1, 999999999)
    
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
        "seed": final_seed
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