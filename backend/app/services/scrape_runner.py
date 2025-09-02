# # backend/app/services/scrape_runner.py
# import os
# import sys
# import json
# from pathlib import Path
# from playwright.sync_api import sync_playwright, TimeoutError
# from dotenv import load_dotenv

# # --- Configurações ---
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_ROOT = os.path.dirname(BASE_DIR)
# if PROJECT_ROOT not in sys.path:
#     sys.path.insert(0, PROJECT_ROOT)

# env_path = Path(PROJECT_ROOT) / ".env"
# if not env_path.exists():
#     raise FileNotFoundError(f".env file not found at {env_path}")
# load_dotenv(dotenv_path=env_path)

# PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL")
# PINTEREST_PASSWORD = os.getenv("PINTEREST_PASSWORD")
# HEADLESS = False  # ⚡ Tela visível no Windows

# def logger(msg: str):
#     # Logs vão para stderr, para não poluir o JSON no stdout
#     print(f"[SCRAPER] {msg}", file=sys.stderr, flush=True)

# def pinterest_login(page, email: str, password: str) -> bool:
#     logger("Abrindo página de login...")
#     page.goto("https://www.pinterest.com/login/", timeout=10000)
#     try:
#         page.wait_for_selector('input[data-test-id="emailInputField"]', timeout=15000)
#         page.wait_for_selector('input[data-test-id="passwordInputField"]', timeout=10000)

#         page.fill('input[data-test-id="emailInputField"]', email)
#         page.fill('input[data-test-id="passwordInputField"]', password)

#         login_button = page.locator('div[data-test-id="registerFormSubmitButton"]')
#         login_button.wait_for(state="visible", timeout=15000)
#         login_button.click(force=True)

#         page.wait_for_selector('[data-test-id="homefeed-feed"]', timeout=20000)
#         logger("✅ Login bem-sucedido no Pinterest!")
#         return True
#     except TimeoutError:
#         logger("❌ Falha no login: verifique usuário/senha ou carregamento da página.")
#         return False
#     except Exception as e:
#         logger(f"❌ Erro inesperado no login: {e}")
#         return False

# def scrape(prompt_text: str):
#     """Função principal de scraping."""
#     try:
#         with sync_playwright() as pw:
#             browser = pw.chromium.launch(headless=HEADLESS, slow_mo=200)
#             page = browser.new_page()

#             if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
#                 raise ValueError("PINTEREST_EMAIL ou PINTEREST_PASSWORD não estão setados no ambiente")

#             if not pinterest_login(page, PINTEREST_EMAIL, PINTEREST_PASSWORD):
#                 browser.close()
#                 return []

#             page.fill('input[data-test-id="search-box-input"]', prompt_text)
#             page.keyboard.press("Enter")
#             page.wait_for_load_state("networkidle")
#             page.wait_for_selector('img', timeout=10000)

#             images = page.query_selector_all("img")[:3]

#             pins = []
#             for i, img in enumerate(images):
#                 src = img.get_attribute("src")
#                 alt = img.get_attribute("alt")
#                 if not src:
#                     continue
#                 pins.append({
#                     "image_url": src,
#                     "title": alt or "",
#                     "pin_url": f"https://pinterest.com/pin/{i}",
#                     "description": alt or ""
#                 })

#             browser.close()
#             logger(f"✅ Scraping concluído: {len(pins)} imagens coletadas.")
#             return pins
#     except Exception as e:
#         logger(f"❌ Erro no scraping: {str(e)}")
#         return []

# if __name__ == "__main__":
#     # Pega o prompt do argumento de linha de comando
#     prompt = sys.argv[1] if len(sys.argv) > 1 else "default-prompt"
#     result = scrape(prompt)
#     # ⚠️ Imprime somente o JSON no stdout
#     print(json.dumps(result), flush=True)



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
HEADLESS = False  # ⚡ Tela visível no Windows

def logger(msg: str):
    # Logs vão para stderr, para não poluir o JSON no stdout
    print(f"[SCRAPER] {msg}", file=sys.stderr, flush=True)

def pinterest_login(page, email: str, password: str) -> bool:
    logger("Abrindo página de login...")
    page.goto("https://www.pinterest.com/login/", timeout=15000)
    try:
        page.wait_for_selector('input[data-test-id="emailInputField"]', timeout=15000)
        page.fill('input[data-test-id="emailInputField"]', email)
        page.fill('input[data-test-id="passwordInputField"]', password)

        login_button = page.locator('div[data-test-id="registerFormSubmitButton"]')
        login_button.wait_for(state="visible", timeout=15000)
        login_button.click(force=True)

        # Espera feed principal carregar
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
    """Função principal de scraping."""
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=HEADLESS, slow_mo=200)
            page = browser.new_page()

            if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
                raise ValueError("PINTEREST_EMAIL ou PINTEREST_PASSWORD não estão setados no ambiente")

            if not pinterest_login(page, PINTEREST_EMAIL, PINTEREST_PASSWORD):
                browser.close()
                return []

            logger(f"🔍 Pesquisando por: {prompt_text}")
            page.fill('input[data-test-id="search-box-input"]', prompt_text)
            page.keyboard.press("Enter")

            # Aguarda container de pins
            num_images=5
            page.wait_for_selector('div[data-test-id="pin"]', timeout=20000)
            pins_elements = page.query_selector_all('div[data-test-id="pin"]')[:num_images+1]

            pins = []
            for i, pin_el in enumerate(pins_elements):
                img = pin_el.query_selector('img')
                if not img:
                    continue
                src = img.get_attribute("src") or img.get_attribute("srcset")
                alt = img.get_attribute("alt") or ""
                if not src:
                    continue
                pins.append({
                    "image_url": src,
                    "title": alt,
                    "pin_url": f"https://pinterest.com/pin/{i}",
                    "description": alt
                })

            browser.close()
            logger(f"✅ Scraping concluído: {len(pins)} imagens coletadas.")
            return pins

    except Exception as e:
        logger(f"❌ Erro no scraping: {str(e)}")
        return []

if __name__ == "__main__":
    # Pega o prompt do argumento de linha de comando
    prompt = sys.argv[1] if len(sys.argv) > 1 else "default-prompt"
    result = scrape(prompt)
    # ⚠️ Imprime somente o JSON no stdout
    print(json.dumps(result), flush=True)
