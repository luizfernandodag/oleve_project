# backend/app/services/scrape_runner.py
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import json
from playwright.sync_api import sync_playwright, TimeoutError
from time import sleep 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/app
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # backend
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
env_path = Path(PROJECT_ROOT) / ".env"
if not env_path.exists():
    raise FileNotFoundError(f".env file not found at {env_path}")

load_dotenv(dotenv_path=env_path)

PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL")
PINTEREST_PASSWORD = os.getenv("PINTEREST_PASSWORD")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
HEADLESS = False


def logger(msg: str):
    print(f"[SCRAPER] {msg}", file=sys.stderr)

def pinterest_login(page, email: str, password: str, pause: bool = False) -> bool:
    """
    Realiza login no Pinterest e retorna True se o login foi bem-sucedido.
    Args:
        page: instância do Playwright page
        email: email do Pinterest
        password: senha do Pinterest
        pause: se True, pausa a execução para depuração (page.pause())
    Returns:
        bool: True se login bem-sucedido, False caso contrário
    """
    logger("Abrindo página de login...")
    page.goto("https://www.pinterest.com/login/", timeout=5000)
    # page.wait_for_timeout(3000)  # espera 3s

    
    logger(f"Página atual após goto: {page.url}")


    try:
        # Espera até que os campos estejam disponíveis
        
        page.wait_for_selector('input[data-test-id="emailInputField"]', timeout=15000)
        page.wait_for_selector('input[data-test-id="passwordInputField"]', timeout=15000)
        page.wait_for_selector('button:has-text("Entrar")', timeout=15000)

        # Preenche email e senha
        logger("Preenchendo email e senha...")
        page.fill('input[data-test-id="emailInputField"]', email)
        page.fill('input[data-test-id="passwordInputField"]', password)

        # Pausa opcional para depuração
        if pause:
            logger("Pausa ativada para depuração...")
            page.pause()

        # Clica no botão "Entrar"
        logger("Clicando no botão Entrar...")
        page.click('button:has-text("Entrar")')

        # Espera até que o feed principal carregue (indicando login bem-sucedido)
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
            logger("Launching browser...")
            browser = pw.chromium.launch(headless=HEADLESS)
            page = browser.new_page(ignore_https_errors=True)

            # page = browser.new_page()

            # PAUSA para inspeção manual antes do login
            # page.pause()

            # Login com credenciais do .env
            if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
                raise ValueError("PINTEREST_EMAIL ou PINTEREST_PASSWORD não estão setados no ambiente")
            elif not pinterest_login(page, PINTEREST_EMAIL, PINTEREST_PASSWORD):
                browser.close()
                return []

            # Pesquisa pins
            search_url = f"https://www.pinterest.com/search/pins/?q={prompt_text}"
            logger(f"Acessando busca: {search_url}")
            page.goto(search_url)
            page.wait_for_load_state("networkidle")

            images = page.query_selector_all("img")

            pins = []
            for i, img in enumerate(images[:10]):  # top 10
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
            logger(f"Scraping concluído: {len(pins)} pins coletados.")
            return pins

    except Exception as e:
        logger(f"Erro no scraping: {str(e)}")
        return []


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "default-prompt"
    result = scrape(prompt)
    print(json.dumps(result))
