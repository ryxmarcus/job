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

        # Let's inspect the entire Address form container HTML
        html = await page.evaluate('''() => {
            const addr = document.querySelector('input[name="addressLine1"]');
            const form = addr ? addr.closest('form, [role="form"], .address-section, fieldset, div[class*="address"]') : null;
            return form ? form.innerHTML : (addr ? addr.parentElement.parentElement.parentElement.outerHTML : null);
        }''')
        print('Address HTML snippet:\n', html[:2000] if html else 'None')

asyncio.run(main())

