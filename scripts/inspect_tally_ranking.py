import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # In Tally, ranking questions have buttons or draggable items
        # Let's inspect all buttons or items under the ranking question
        items = await pg.evaluate("""() => {
            let res = [];
            document.querySelectorAll('[data-rbd-draggable-id], [class*="ranking"], [class*="draggable"], button').forEach(el => {
                let t = el.innerText.trim();
                if (t) res.push({ tag: el.tagName, class: el.className, text: t.replace(/\\n/g, ' -- ') });
            });
            return res;
        }""")
        print(f"Interactive / draggable items found: {len(items)}")
        for it in items:
            print("  *", it)

if __name__ == '__main__':
    asyncio.run(main())

