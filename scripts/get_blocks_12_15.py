import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        items = await pg.evaluate("""() => {
            let container = document.querySelector('.tally-block-ec89cb7a-c9b9-4ba7-9bbf-7e4c1ef9dffb').parentElement;
            return [11, 12, 13, 14, 15, 16].map(idx => {
                let c = container.children[idx];
                return {
                    idx: idx,
                    class: c ? c.className : 'null',
                    html: c ? c.outerHTML : 'null'
                };
            });
        }""")
        for it in items:
            print(f"--- CHILD {it['idx']} ({it['class']}) ---")
            print(it['html'][:500])

if __name__ == '__main__':
    asyncio.run(main())

