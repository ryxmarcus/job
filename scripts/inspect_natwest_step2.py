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

        print('At NatWest step 2')
        await asyncio.sleep(2) # wait for loadings to settle

        # Check all inputs and selects
        inputs = await natwest_page.query_selector_all('input, button[aria-haspopup="listbox"], select')
        print(f'Total inputs found: {len(inputs)}')
        for inp in inputs:
            d_id = await inp.get_attribute('data-automation-id') or await inp.get_attribute('id') or ''
            val = ''
            if await inp.evaluate('e => e.tagName') == 'INPUT':
                val = await inp.input_value()
            txt = (await inp.text_content() or '').strip()
            print(f'Input [{d_id}]: val="{val}", txt="{txt}"')

asyncio.run(main())

