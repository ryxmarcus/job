import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Inspect all radios and ranking inputs
        radios = await pg.query_selector_all('input[type="radio"]')
        print(f"Total radio inputs: {len(radios)}")

        # Check ranking items
        ranking_items = await pg.evaluate("""() => {
            let res = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.innerText && el.innerText.includes('Rank from 1')) {
                    res.push(el.parentElement.innerText);
                }
            });
            return res;
        }""")
        print("\nRanking question container:\n", ranking_items[0] if ranking_items else "Not found")

if __name__ == '__main__':
    asyncio.run(main())

