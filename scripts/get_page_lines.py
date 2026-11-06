import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        # Click college input
        col_inp = await pg.query_selector('input[placeholder*="Search for your college"]')
        if col_inp:
            await col_inp.click()
            await asyncio.sleep(1)
            
            # Print all visible text on the page right now
            body = await pg.inner_text('body')
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            for l in lines:
                print("LINE:", l)

if __name__ == '__main__':
    asyncio.run(main())

