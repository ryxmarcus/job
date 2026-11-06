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

        # Check what options or list items are visible in cx-select
        items = await page.query_selector_all('.cx-select__list-item, [role="row"], [role="gridcell"], [role="option"]')
        print(f'Items found: {len(items)}')
        for it in items:
            t = (await it.text_content() or '').strip()
            print('Item:', t)
            if '110085' in t or 'Delhi' in t or 'Rohini' in t:
                print('Clicking matching pin item:', t)
                await it.click()
                break

asyncio.run(main())

