import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        indicators = await pg.query_selector_all('.tally-required-indicator')
        print(f"Total required indicators: {len(indicators)}")
        for idx, ind in enumerate(indicators):
            parent = await ind.evaluate("""el => {
                let p = el.parentElement;
                return p ? p.innerText.trim().replace(/\\n/g, ' ') : '';
            }""")
            print(f"[{idx}] {parent[:90]}")

if __name__ == '__main__':
    asyncio.run(main())

