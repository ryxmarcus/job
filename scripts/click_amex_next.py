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
            if 'careers.americanexpress.com' in p_elem.url and 'section' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        print('At AMEX URL:', page.url)
        # Check Next button
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next on Step 1...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Next:', page.url)
            txt = await page.inner_text('body')
            print('Body preview:\n', txt[:500])

asyncio.run(main())
