import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        res = await pg.evaluate("""() => {
            let inds = document.querySelectorAll('.tally-required-indicator');
            let el5 = inds[5];
            
            // Collect all parent elements of el5
            let parents = [];
            let p = el5;
            while (p) {
                parents.push({ tag: p.tagName, class: p.className, id: p.id });
                p = p.parentElement;
            }
            return parents;
        }""")
        print("Parents of indicator 5:")
        for p in res:
            print(" ", p)

if __name__ == '__main__':
    asyncio.run(main())

