# backend/app/services/warmup_runner.py
import os
import sys
import json
import openai
from playwright.sync_api import sync_playwright

# -------------------------------
# Ajuste de path para rodar standalone
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/app
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # backend
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

# -------------------------------
# Logger
# -------------------------------
def logger(msg: str):
    print(f"[WARMUP] {msg}")

# -------------------------------
# Warmup síncrono
# -------------------------------
def warmup(prompt_text: str):
    try:
        logger("Launching Playwright browser...")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.pinterest.com")
            logger("Pinterest page loaded successfully.")

            # Exemplo de prompt OpenAI
            sample_image_url = "https://via.placeholder.com/150"
            logger("Sending prompt to OpenAI API...")

            response = openai.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Score this image for interior design."},
                    {
                        "role": "user",
                        "content": (
                            f"Prompt: {prompt_text}\n\n"
                            f"Image: {sample_image_url}\n\n"
                            "Dê uma nota de 0 a 10 para a estética e relevância do design."
                        ),
                    },
                ],
            )

            if response.choices and len(response.choices) > 0:
                score = response.choices[0].message.content
                logger(f"Score returned: {score}")
                return {"success": True, "score": score}
            else:
                logger("Unexpected response from OpenAI API.")
                return {"success": False, "error": "Unexpected response format."}

    except Exception as e:
        logger(f"Error during warmup: {str(e)}")
        return {"success": False, "error": str(e)}

# -------------------------------
# Executa standalone
# -------------------------------
if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "startup-check"
    result = warmup(prompt)
    print(json.dumps(result))
