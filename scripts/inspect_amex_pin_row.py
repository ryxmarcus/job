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

        print('Found AMEX page!')
        # Let's inspect the postal code input and the entire parent row
        pin_el = await page.query_selector('input[name="postalCode"]')
        if pin_el:
            row_html = await pin_el.evaluate('e => e.closest(".input-row").outerHTML')
            print('Postal row HTML:\n', row_html)

asyncio.run(main())

