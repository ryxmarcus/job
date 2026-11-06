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
            if 'careers.americanexpress.com' in p_elem.url and 'section/1' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX section 1 page not found!')
            return

        pin_input = await page.query_selector('input[name="postalCode"]')
        if pin_input:
            print('Clicking pin input...')
            await pin_input.click()
            await pin_input.focus()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await pin_input.type('110085', delay=100)
            await asyncio.sleep(2)
            # Press Enter or Tab
            await page.keyboard.press('Enter')
            await asyncio.sleep(1)

        # Check Next button
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Next:', page.url)

asyncio.run(main())

