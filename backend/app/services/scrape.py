import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright
from ..config import settings

async def scrape_pinterest(prompt: str, logger, max_pins: int = 25):
    logger("scrape:start")
    results = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=settings.HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()
        url = f"https://www.pinterest.com/search/pins/?q={quote(prompt)}"
        await page.goto(url)
        await page.wait_for_selector('img', timeout=20000)
        seen = set()
        while len(results) < max_pins:
            cards = page.locator('a[href*="/pin/"]')
            count = await cards.count()
            for i in range(min(count, max_pins*3)):
                try:
                    handle = cards.nth(i)
                    pin_url = await handle.get_attribute('href')
                    if not pin_url: continue
                    if pin_url.startswith('/'):
                        pin_url = 'https://www.pinterest.com' + pin_url
                    if pin_url in seen: continue
                    seen.add(pin_url)
                    image = handle.locator('img')
                    image_url = await image.get_attribute('src') or ""
                    title = await image.get_attribute('alt') or ""
                    if image_url:
                        results.append({
                            'title': title,
                            'image_url': image_url,
                            'pin_url': pin_url,
                            'description': title
                        })
                        logger(f"scrape:collected:{len(results)}")
                        if len(results) >= max_pins: break
                except Exception:
                    continue
            await page.mouse.wheel(0, 1800)
            await asyncio.sleep(1.0)
        await context.close()
        await browser.close()
    logger("scrape:done")
    return results[:max_pins]
