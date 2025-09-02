# backend/app/services/scrape_runner.py
import os
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import json

from playwright.async_api import async_playwright, TimeoutError
from .validate import score_image  # função assíncrona de scoring

# -----------------------
# Config
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

PINTEREST_EMAIL = os.getenv("PINTEREST_EMAIL")
PINTEREST_PASSWORD = os.getenv("PINTEREST_PASSWORD")
HEADLESS = True

# -----------------------
# Logger simples
# -----------------------
def logger(msg: str):
    print(f"[SCRAPER] {msg}", flush=True)

# -----------------------
# Login Pinterest
# -----------------------
async def pinterest_login(page, email: str, password: str) -> bool:
    logger("Abrindo página de login...")
    await page.goto("https://www.pinterest.com/login/", timeout=15000)
    try:
        await page.fill('input[data-test-id="emailInputField"]', email)
        await page.fill('input[data-test-id="passwordInputField"]', password)
        await page.click('div[data-test-id="registerFormSubmitButton"]', force=True)
        await page.wait_for_selector('[data-test-id="homefeed-feed"]', timeout=20000)
        logger("✅ Login bem-sucedido!")
        return True
    except TimeoutError:
        logger("❌ Falha no login")
        return False

# -----------------------
# Scraping + validação AI
# -----------------------
async def scrape_and_validate(prompt_text: str):
    if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
        raise ValueError("PINTEREST_EMAIL ou PINTEREST_PASSWORD não setados")

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=HEADLESS)
            page = await browser.new_page()

            if not await pinterest_login(page, PINTEREST_EMAIL, PINTEREST_PASSWORD):
                await browser.close()
                return []

            # Pesquisa
            await page.fill('input[data-test-id="search-box-input"]', prompt_text)
            await page.keyboard.press("Enter")
            await page.wait_for_selector('div[data-test-id="pin"]', timeout=20000)

            # Coleta de pins
            pins_elements = await page.query_selector_all('div[data-test-id="pin"]')
            pins = []
            for i, pin_el in enumerate(pins_elements[:30]):
                img = await pin_el.query_selector('img')
                if not img: 
                    continue
                src = await img.get_attribute("src") or await img.get_attribute("srcset")
                alt = await img.get_attribute("alt") or ""
                if not src: 
                    continue
                pins.append({
                    "image_url": src,
                    "title": alt,
                    "pin_url": f"https://pinterest.com/pin/{i}",
                    "description": alt
                })

            await browser.close()
            logger(f"✅ Scraping concluído: {len(pins)} imagens coletadas.")

        # Validação AI assíncrona (score_image deve estar atualizado para usar OpenAI async)
        validated_pins = await asyncio.gather(*[score_image(prompt_text, pin) for pin in pins])
        return validated_pins

    except Exception as e:
        logger(f"❌ Erro: {e}")
        return []
