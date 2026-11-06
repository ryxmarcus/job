import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        natwest_page = None
        for p_elem in context.pages:
            if 'rbs.wd3.myworkdayjobs.com' in p_elem.url:
                natwest_page = p_elem
                break
        if not natwest_page:
            print('NatWest page not found!')
            return

        controls = await natwest_page.query_selector_all('input, button[aria-haspopup="listbox"], select')
        print(f'Total controls on step 5: {len(controls)}')
        for c in controls:
            c_id = await c.get_attribute('id') or ''
            c_type = await c.get_attribute('type') or ''
            aria = await c.get_attribute('aria-label') or ''
            txt = (await c.text_content() or '').strip()
            print(f'Ctrl: id={c_id}, type={c_type}, aria={aria}, txt={txt}')

asyncio.run(main())

