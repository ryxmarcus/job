import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = await context.new_page()

        url = 'https://job-boards.greenhouse.io/particle41llc/jobs/5018960008'
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)

        # Inspect inputs
        inputs = await page.query_selector_all('input, select, textarea')
        print(f"Found {len(inputs)} input elements:")
        for inp in inputs:
            t = await inp.evaluate('e => e.tagName')
            itype = await inp.get_attribute('type') or ''
            name = await inp.get_attribute('name') or ''
            id_attr = await inp.get_attribute('id') or ''
            aria_label = await inp.get_attribute('aria-label') or ''
            print(f"  Tag={t}, type={itype}, id={id_attr}, name={name}, aria={aria_label}")

if __name__ == '__main__':
    asyncio.run(main())

