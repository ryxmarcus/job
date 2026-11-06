import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        html = await pg.evaluate("""() => {
            let el = document.querySelector('.tally-required-indicator');
            let p = el.parentElement;
            let siblings = Array.from(p.children).map(c => ({
                tag: c.tagName,
                class: c.className,
                text: c.innerText.trim().replace(/\\n/g, ' ')
            }));
            return siblings;
        }""")
        print("Siblings of required indicator:")
        for s in html:
            print(" ", s)

if __name__ == '__main__':
    asyncio.run(main())

