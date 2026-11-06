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

        print('NatWest URL:', natwest_page.url)
        print('NatWest Title:', await natwest_page.title())
        # Let's inspect buttons / form on NatWest page
        text = await natwest_page.inner_text('body')
        print('NatWest body preview:\n', text[:800])

asyncio.run(main())

