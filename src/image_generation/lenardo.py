import time
import requests

# --- CONFIGURATION ---
LEONARDO_API_KEY = "6cd1bf74-0792-4738-9828-5b7fb1e9ea67"  # Get this from Leonardo Settings

# --- LEONARDO AI HELPER FUNCTIONS ---
def generate_image_leonardo(prompt):
    """
    Sends a prompt to Leonardo AI and waits for the image URL.
    """
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {LEONARDO_API_KEY}"
    }

    # 1. SEND GENERATION REQUEST
    payload = {
        "prompt": prompt,
        "modelId": "de7d3faf-762f-48e0-b3b7-9d0ac3a3fcf3", # Leonardo Phoenix (Great for text adherence)
        # OR use "d69c8273-6b17-4a30-a13e-d6637ae1c644" for 3D Animation Style
        "width": 1024,
        "height": 576, # 16:9 Aspect Ratio (Cinematic)
        "num_images": 1,
        "presetStyle": "CINEMATIC"
        # "promptMagic": True
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Leonardo Error: {response.text}")
        return None

    generation_id = response.json()['sdGenerationJob']['generationId']
    print(f"      🎨 Job ID: {generation_id} (Waiting for Leonardo...)", end="", flush=True)

    # 2. POLL FOR COMPLETION (Wait loop)
    # Leonardo takes 10-30 seconds to generate
    image_url = None
    wait_time = 0
    
    while wait_time < 60: # Max wait 60 seconds
        time.sleep(4)
        wait_time += 4
        print(".", end="", flush=True)
        
        status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        status_response = requests.get(status_url, headers=headers)
        
        data = status_response.json()
        job_status = data['generations_by_pk']['status']
        
        if job_status == 'COMPLETE':
            # Get the URL of the first image
            image_url = data['generations_by_pk']['generated_images'][0]['url']
            print(" Done!")
            break
        elif job_status == 'FAILED':
            print(" Failed!")
            break
            
    return image_url

def download_image(url, save_path):
    img_data = requests.get(url).content
    with open(save_path, 'wb') as handler:
        handler.write(img_data)

visual = "      "
image_url = generate_image_leonardo("visual")
download_image(image_url, "joseph.png")