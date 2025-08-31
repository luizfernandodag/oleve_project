# backend/app/services/warmup.py
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from ..config import settings

LOGIN_URL = "https://www.pinterest.com/login/"
SEARCH_URL = "https://www.pinterest.com/search/pins/?q={query}"

async def warmup_pinterest(prompt: str, logger):
    """
    Scrapes Pinterest based on a search prompt.
    
    Steps:
    1. Login using credentials from settings.
    2. Search for the given prompt.
    3. Scroll the page to load pins.
    4. Visit top pins and attempt to click "Save" button.
    """
    logger("warmup:start")
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=settings.HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Login
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
            await browser.close()
            return
        except Exception as e:
            logger(f"warmup:login-error:{e}")
            await browser.close()
            return

        # Prepare search query
        q = prompt.replace(" ", "%20")
        await page.goto(SEARCH_URL.format(query=q))
        try:
            await page.wait_for_selector('img', timeout=20000)
        except PlaywrightTimeoutError:
            logger("warmup:search-timeout")
            await browser.close()
            return

        # Scroll to load pins
        for _ in range(4):
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(1.1)

        # Visit top pins and try to save
        try:
            links = await page.locator('a[href*="/pin/"]').evaluate_all(
                "els => els.slice(0,5).map(e => e.href)"
            )
            for link in links:
                logger(f"warmup:visit:{link}")
                await page.goto(link)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(0.8)
                try:
                    save_btn = page.locator('button:has-text("Save")')
                    if await save_btn.count() > 0:
                        await save_btn.first.click()
                        logger("warmup:saved")
                        await asyncio.sleep(0.5)
                    else:
                        logger("warmup:no-save-button")
                except Exception as e:
                    logger(f"warmup:save-error:{e}")
        except Exception as e:
            logger(f"warmup:enumeration-failed:{e}")

        # Close browser
        await context.close()
        await browser.close()
        logger("warmup:done")
