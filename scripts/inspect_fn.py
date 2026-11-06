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

        el = await natwest_page.query_selector('[data-automation-id*="firstName"]')
        if el:
            tag = await el.evaluate('e => e.tagName')
            html = await el.evaluate('e => e.outerHTML')
            print(f'Tag: {tag}, HTML: {html}')
        else:
            print('firstName not found by data-automation-id!')

asyncio.run(main())

