# backend/app/services/warmup.py
import asyncio
import sys

import openai
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from ..config import settings

openai.api_key = settings.OPENAI_API_KEY

LOGIN_URL = "https://www.pinterest.com/login/"
SEARCH_URL = "https://www.pinterest.com/search/pins/?q={query}"

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def warmup_pinterest(prompt: str, logger):
    logger("warmup:start")
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=settings.HEADLESS)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Login
            try:
                await page.goto(LOGIN_URL)
                await page.wait_for_selector('input[name="id"]', timeout=20000)
                await page.fill('input[name="id"]', settings.PINTEREST_EMAIL)
                await page.fill('input[name="password"]', settings.PINTEREST_PASSWORD)
                await page.click('button[type="submit"]')
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                logger("warmup:login-success")
            except PlaywrightTimeoutError:
                logger("warmup:login-timeout")
                return
            except Exception as e:
                logger(f"warmup:login-error:{e}")
                return

            # Simula scraping e scoring via OpenAI
            query = prompt.replace(" ", "%20")
            await page.goto(SEARCH_URL.format(query=query))
            try:
                await page.wait_for_selector('img', timeout=20000)
                # Exemplo fictício de validação OpenAI
                import json
                sample_image_url = "https://via.placeholder.com/150"
                response = openai.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "Score this image for interior design."},
                        {"role": "user", "content": f"Prompt: {prompt}"},
                        {"role": "user", "content": f"Image URL: {sample_image_url}"}
                    ],
                    temperature=0
                )
                result_text = response.choices[0].message.content
                result_json = json.loads(result_text)
                logger(f"warmup:sample_pin_score: {result_json}")
            except Exception as e:
                logger(f"warmup:scoring-error:{e}")

            await context.close()
            await browser.close()
            logger("warmup:done")
    except Exception as e:
        logger(f"[Warmup Fatal Error] {e}")
