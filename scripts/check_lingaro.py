import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        lingaro_page = None
        for p in context.pages:
            if 'lingarogroup' in p.url:
                lingaro_page = p
                break
        if not lingaro_page:
            print('Lingaro page not found!')
            return

        print('Lingaro URL:', lingaro_page.url)
        # Find any validation errors or required empty fields
        errors = await lingaro_page.query_selector_all('.error, [aria-invalid="true"], .application-error')
        print(f'Errors found: {len(errors)}')
        for e in errors:
            print('Error text:', await e.text_content())

        # Check required fields
        req = await lingaro_page.query_selector_all('input[required], select[required], textarea[required]')
        print(f'Required fields: {len(req)}')
        for r in req:
            tag = await r.evaluate('e => e.tagName')
            name = await r.get_attribute('name') or ''
            val = await r.input_value() if tag == 'INPUT' else ''
            print(f'  Req [{tag}] name={name}, val="{val}"')

asyncio.run(main())

