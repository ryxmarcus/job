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

        reg = await page.query_selector('input[name="region2"]')
        pin = await page.query_selector('input[name="postalCode"]')
        reg_b = await reg.bounding_box() if reg else None
        pin_b = await pin.bounding_box() if pin else None
        print('reg box:', reg_b)
        print('pin box:', pin_b)

        # Let's click on the State input box
        if reg_b:
            await page.mouse.click(reg_b['x'] + 50, reg_b['y'] + reg_b['height'] / 2)
            await asyncio.sleep(1)
            # Take screenshot
            await page.screenshot(path='job/amex_reg_clicked.png')
            print('Clicked State input and saved screenshot')

asyncio.run(main())

