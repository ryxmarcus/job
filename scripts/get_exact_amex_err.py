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

        # Check all error messages or alert banners
        banner = await page.query_selector('.banner, [role="alert"], .oj-messaging-inline-message-summary, .oj-form-control-inline-message')
        if banner:
            print('Banner / message:', await banner.text_content())
        
        # Let's see all text content inside all elements with class containing 'message' or 'error'
        errs = await page.query_selector_all('[class*="message"], [class*="error"], [class*="invalid"]')
        print(f'Total message elements: {len(errs)}')
        for e in errs:
            t = (await e.text_content() or '').strip()
            if t and len(t) < 200:
                print('Error/msg:', t)

asyncio.run(main())

