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
            if 'careers.americanexpress.com' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX page not found!')
            return

        # Check all alerts / invalid elements
        invalids = await page.query_selector_all('.oj-invalid, [aria-invalid="true"], .oj-messaging-inline')
        print(f'Invalid elements count: {len(invalids)}')
        for inv in invalids:
            print('Invalid element:', (await inv.text_content() or '').strip())

        # Check value of region2 and postalCode
        reg = await page.query_selector('input[name="region2"]')
        pin = await page.query_selector('input[name="postalCode"]')
        print('Region val:', await reg.input_value() if reg else None)
        print('PostalCode val:', await pin.input_value() if pin else None)

asyncio.run(main())

