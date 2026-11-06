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

        pin = await page.query_selector('input[name="postalCode"]')
        if pin:
            print('Typing 110085 into Pin Code...')
            await pin.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await pin.type('110085', delay=100)
            await asyncio.sleep(2)

        # Screenshot to see the dropdown for 110085
        await page.screenshot(path='job/amex_pin_typed.png')
        print('Screenshot saved to job/amex_pin_typed.png')

asyncio.run(main())

