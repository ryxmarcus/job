import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Use index-based or input selector
        inps = await pg.query_selector_all('input')
        print(f"Total inputs on page: {len(inps)}")
        # inps[8] is the college name text input
        await inps[8].fill('Delhi Technological University (DTU)')
        print("Filled college name via inps[8]: Delhi Technological University (DTU)")

        await asyncio.sleep(1)

        # Clear the 'Search for your college' input so it doesn't conflict
        await inps[6].fill('')

        # Click Next button
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Clicking Next button...")
            await next_btn.click()
            await asyncio.sleep(3)
            print("\nPage text after Next:\n" + "="*50)
            txt = await pg.inner_text('body')
            print(txt[:1500])
            print("="*50)

if __name__ == '__main__':
    asyncio.run(main())

