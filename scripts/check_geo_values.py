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
            if 'job/26015724/apply' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        c = await page.eval_on_selector('input[name="country"]', 'e => e.value')
        r = await page.eval_on_selector('input[name="region2"]', 'e => e.value')
        ci = await page.eval_on_selector('input[name="city"]', 'e => e.value')
        p = await page.eval_on_selector('input[name="postalCode"]', 'e => e.value')
        print(f'Country: "{c}", Region/State: "{r}", City: "{ci}", PostalCode: "{p}"')

asyncio.run(main())

