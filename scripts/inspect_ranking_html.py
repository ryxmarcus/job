import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # Find the ranking question container
        html = await pg.evaluate("""() => {
            let el = Array.from(document.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('Rank from 1'));
            return el ? el.parentElement.innerHTML : 'Not found';
        }""")
        print("RANKING QUESTION HTML SNIPPET:\n" + "="*50)
        print(html[:2000])
        print("="*50)

if __name__ == '__main__':
    asyncio.run(main())

