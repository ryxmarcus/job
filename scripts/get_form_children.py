import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        children = await pg.evaluate("""() => {
            let container = document.querySelector('.tally-block-ec89cb7a-c9b9-4ba7-9bbf-7e4c1ef9dffb').parentElement;
            return Array.from(container.children).map(c => ({
                class: c.className,
                text: c.innerText ? c.innerText.trim().replace(/\\n/g, ' ').substring(0, 80) : ''
            }));
        }""")
        print(f"Total blocks in form: {len(children)}")
        for idx, c in enumerate(children):
            if 'ec89cb7a' in c['class'] or idx > 15:
                print(f"[{idx}] {c['class']} -> {c['text']}")

if __name__ == '__main__':
    asyncio.run(main())

