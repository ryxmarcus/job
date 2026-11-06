import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for page in context.pages:
            if 'careers.americanexpress.com' in page.url and 'section' in page.url:
                btn = await page.query_selector('button:has-text("RESUME APPLICATION"), a:has-text("RESUME APPLICATION")')
                if btn:
                    print('Clicking RESUME APPLICATION...')
                    await btn.click()
                    await asyncio.sleep(4)
                    print('URL after resume:', page.url)
                    txt = await page.inner_text('body')
                    print('Body:\n', txt[:400])

asyncio.run(main())

