# 🤖 AI Telugu Bible Story Generator & Uploader

**Automated YouTube Channel Pipeline using GenAI (Llama 3, SDXL, EdgeTTS)**

This project is an end-to-end AI automation pipeline that generates, animates, and uploads Telugu Bible stories to YouTube. It uses a **"One-Shot Glossary Injection"** technique to ensure accurate Biblical terminology in Telugu while generating high-quality 3D Disney-style visuals in English.

---

## 🚀 Features

* **Bilingual Intelligence:** Uses **Llama-3-70b** (via Groq) to generate Telugu narration and English visual prompts simultaneously.
* **Biblical Accuracy:** Implements a strict glossary system to ensure names like "Joseph" become "యోసేపు" (Yosepu) instead of literal translations.
* **Grandmother Persona:** The AI narrates in a "Chandamama Kathalu" style (Ammamma persona) to make stories interactive and emotional for children.
* **High-Quality Visuals:** Uses **DreamShaper XL (SDXL)** for cinematic, 3D Pixar-style animation.
* **Ken Burns Animation:** Applies dynamic pan/zoom effects to static images using `MoviePy`.
* **Auto-Upload:** Automatically uploads the final rendered video to YouTube with metadata using OAuth 2.0.

---

## 🛠️ Tech Stack

* **Core Logic:** Python 3.10
* **LLM (The Brain):** Llama-3-70b-Versatile (via Groq API)
* **Image Gen (The Artist):** Stable Diffusion XL (DreamShaper) via HuggingFace Diffusers
* **TTS (The Voice):** Edge-TTS (Microsoft Azure Neural Voices - `te-IN-ShrutiNeural`)
* **Video Processing:** MoviePy
* **Infrastructure:** Google Colab / AWS SageMaker (T4 GPU)
* **YouTube API:** Google OAuth 2.0 for automated uploads

---

## ⚙️ Setup & Installation

### Prerequisite: API Keys
You need the following keys (free tiers available):
1.  **Groq API Key:** For the LLM logic.
2.  **Google Cloud OAuth Credentials:** For YouTube uploads (`client_secrets.json`).

### Step 1: Local Authentication (YouTube)
Since Colab/SageMaker cannot open a browser, run this script locally to generate your login token.

1.  Download `client_secrets.json` from Google Cloud Console.
2.  Run the auth script:
    ```bash
    pip install google-auth-oauthlib google-api-python-client
    python auth_local.py
    ```
3.  This generates a `token.json` file. Save this file.

### Step 2: Run the Bot (Cloud)
1.  Open `BibleBot_Colab.ipynb` in Google Colab or AWS SageMaker.
2.  Upload `token.json` to your environment (e.g., Google Drive).
3.  Set your `GROQ_API_KEY` in the configuration cell.
4.  Run all cells.

---

## 🧠 Core Logic Overview

### 1. One-Shot Glossary Injection
Instead of translating English to Telugu (which causes errors), the bot injects a terminology map into the system prompt:

```python
glossary = """
- God -> దేవుడు (Devudu)
- Joseph -> యోసేపు (Yosepu)
...
"""