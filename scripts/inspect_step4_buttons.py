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

        buttons = await natwest_page.query_selector_all('button[aria-haspopup="listbox"], button[id*="question"], select, input[type="radio"]')
        print(f'Total question controls: {len(buttons)}')
        for b in buttons:
            b_id = await b.get_attribute('id') or ''
            b_name = await b.get_attribute('name') or ''
            b_aria = await b.get_attribute('aria-label') or ''
            txt = (await b.text_content() or '').strip()
            print(f'Control: id={b_id}, name={b_name}, aria={b_aria}, txt={txt}')

asyncio.run(main())

