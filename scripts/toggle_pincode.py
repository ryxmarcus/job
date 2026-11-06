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

        # Click the toggle button for pin code
        toggle = await page.query_selector('#postalCode-59-toggle-button')
        if toggle:
            print('Clicking postal code toggle button...')
            await toggle.click()
            await asyncio.sleep(2)
            # Find what appeared on the page (like a table, grid, dialog or popup)
            popup_elems = await page.query_selector_all('[role="dialog"], [role="grid"], [role="listbox"], table, tr, td, li')
            print(f'Popup elements count: {len(popup_elems)}')
            for el in popup_elems:
                t = (await el.text_content() or '').strip()
                if t and len(t) < 100:
                    print('Popup elem:', t)
                    if any(x in t for x in ['1100', '110', '122', 'Delhi', 'PIN']):
                        print('Found potential pin match:', t)
                        await el.click()
                        break

asyncio.run(main())

