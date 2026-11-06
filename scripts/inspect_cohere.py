import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        
        pg = await ctx.new_page()
        url = 'https://job-boards.greenhouse.io/coherehealth/jobs/8037633003'
        print(f"Navigating to Cohere Health: {url}...")
        await pg.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(2)

        # Inspect labels
        labels = await pg.query_selector_all('label')
        print(f"Found {len(labels)} labels:")
        for l in labels:
            t = (await l.inner_text()).strip().replace('\n', ' ')
            f = await l.get_attribute('for') or ''
            print(f"  for={f} | {t}")

if __name__ == '__main__':
    asyncio.run(main())

