import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        inp = await pg.query_selector('input[placeholder*="Search for your college"]')
        if inp:
            await inp.click()
            await inp.fill('DTU')
            await asyncio.sleep(1)
            # Find all elements that appeared on the page that were not there before
            all_text = await pg.inner_text('body')
            lines = [l.strip() for l in all_text.split('\n') if l.strip()]
            for l in lines:
                if 'dtu' in l.lower() or 'delhi' in l.lower() or 'technological' in l.lower():
                    print("MATCH:", l)

if __name__ == '__main__':
    asyncio.run(main())

