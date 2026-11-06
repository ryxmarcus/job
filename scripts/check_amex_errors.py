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

        print('Current URL:', page.url)
        # Find all alert / error messages
        alerts = await page.query_selector_all('[role="alert"], .error, .oj-invalid, [aria-invalid="true"]')
        print(f'Total alerts: {len(alerts)}')
        for a in alerts:
            t = (await a.text_content() or '').strip()
            if t:
                print('Alert:', t)

        # Print all inputs with empty values that might be required
        inputs = await page.query_selector_all('input')
        for inp in inputs:
            req = await inp.get_attribute('required') or await inp.get_attribute('aria-required')
            name = await inp.get_attribute('name') or ''
            id_val = await inp.get_attribute('id') or ''
            val = await inp.input_value()
            if req == 'true' or req == '':
                print(f'Required Field: name={name}, id={id_val}, value={val}')

asyncio.run(main())

