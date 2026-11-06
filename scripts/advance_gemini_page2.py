import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Fill Other college name
        col_name = await pg.query_selector('[id="c46ead76-1841-4b10-a7d0-1f3eb1752f9f"], [id*="c46ead76"]')
        if col_name:
            await col_name.fill('Delhi Technological University (DTU)')
            print("Filled Other College Name: Delhi Technological University (DTU)")

        await asyncio.sleep(1)

        # Click Next button
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Found Next button, clicking...")
            await next_btn.click()
            await asyncio.sleep(3)
            print("Current page text snippet after Next:")
            txt = await pg.inner_text('body')
            print(txt[:1000])

if __name__ == '__main__':
    asyncio.run(main())

