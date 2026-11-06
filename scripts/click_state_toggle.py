import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = None
        for p_elem in context.pages:
            if 'job/26015724/apply' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        # Find the State container
        state_toggle = await page.query_selector('button[id*="region2"][id*="toggle"]')
        if state_toggle:
            print('Clicking State toggle button...')
            await state_toggle.click()
            await asyncio.sleep(1)

            # Let's take screenshot of the open dropdown
            await page.screenshot(path='job/amex_state_open.png', full_page=False)
            print('State open screenshot saved!')

asyncio.run(main())

