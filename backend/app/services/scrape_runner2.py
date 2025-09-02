# backend/app/services/scrape_runner.py
import os
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv

# --- Configurações ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

env_path = Path(PROJECT_ROOT) / ".env"
if not env_path.exists():
    raise FileNotFoundError(f".env file not found at {env_path}")
load_dotenv(dotenv_path=env_path)

PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL")
PINTEREST_PASSWORD = os.getenv("PINTEREST_PASSWORD")
HEADLESS = False  # tela visível

def logger(msg: str):
    print(f"[SCRAPER] {msg}", file=sys.stderr)

def pinterest_login(page, email: str, password: str) -> bool:
    logger("Abrindo página de login...")
    page.goto("https://www.pinterest.com/login/", timeout=5000)
    try:
        page.wait_for_selector('input[data-test-id="emailInputField"]', timeout=15000)
        page.wait_for_selector('input[data-test-id="passwordInputField"]', timeout=10000)
        page.wait_for_selector('button:has-text("Entrar")', timeout=2000)

        page.fill('input[data-test-id="emailInputField"]', email)
        page.fill('input[data-test-id="passwordInputField"]', password)

        login_button = page.locator('div[data-test-id="registerFormSubmitButton"]')
        login_button.wait_for(state="visible", timeout=15000)
        login_button.click(force=True)
        page.wait_for_selector('[data-test-id="homefeed-feed"]', timeout=20000)

        logger("✅ Login bem-sucedido no Pinterest!")
        return True
    except TimeoutError:
        logger("❌ Falha no login: verifique usuário/senha ou carregamento da página.")
        return False
    except Exception as e:
        logger(f"❌ Erro inesperado no login: {e}")
        return False

def scrape(prompt_text: str):
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=HEADLESS)
            page = browser.new_page()

            if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
                raise ValueError("PINTEREST_EMAIL ou PINTEREST_PASSWORD não estão setados no ambiente")
            if not pinterest_login(page, PINTEREST_EMAIL, PINTEREST_PASSWORD):
                browser.close()
                return []

            page.fill('input[data-test-id="search-box-input"]', prompt_text)
            page.keyboard.press("Enter")
            page.wait_for_load_state("networkidle")
            page.wait_for_selector('img', timeout=10000)

            images = page.query_selector_all("img")[:3]

            pins = []
            for i, img in enumerate(images):
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if not src:
                    continue
                pins.append({
                    "image_url": src,
                    "title": alt or "",
                    "pin_url": f"https://pinterest.com/pin/{i}",
                    "description": alt or ""
                })

            browser.close()
            logger(f"Scraping concluído: {len(pins)} imagens coletadas.")
            return pins
    except Exception as e:
        logger(f"Erro no scraping: {str(e)}")
        return []

if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "default-prompt"
    result = scrape(prompt)
    print(json.dumps(result))
