import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Search for elements containing the ranking texts
        res = await pg.evaluate("""() => {
            let matches = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.innerText && el.innerText.includes('A one-time high-visibility')) {
                    matches.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        text: el.innerText.trim().replace(/\\n/g, ' ')
                    });
                }
            });
            return matches;
        }""")
        print(f"Ranking element matches found: {len(res)}")
        for m in res:
            print(" ", m)

if __name__ == '__main__':
    asyncio.run(main())

