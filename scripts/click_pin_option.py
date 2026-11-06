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
            print('Clicking pin input...')
            await pin.click()
            await asyncio.sleep(1)

        # Look for option in popup
        opt = await page.query_selector('.cx-select__list-item, [role="row"]:has-text("110085"), [role="option"]:has-text("110085"), div:has-text("110085, DL")')
        if opt:
            print('Found option, clicking it!')
            await opt.click()
            await asyncio.sleep(1)
        else:
            # Try keyboard press ArrowDown then Enter
            print('Trying keyboard ArrowDown + Enter...')
            await page.keyboard.press('ArrowDown')
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            await asyncio.sleep(1)

        # Now click Next on Section 1
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next on Section 1...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Section 1 Next:', page.url)

asyncio.run(main())

