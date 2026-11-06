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

        await asyncio.sleep(4)
        print('Final URL:', page.url)
        print('Final Title:', await page.title())
        txt = await page.inner_text('body')
        print('Final Body Text:\n', txt[:800])
        await page.screenshot(path='job/amex_submitted_final_screen.png')
        print('Saved job/amex_submitted_final_screen.png')

asyncio.run(main())

