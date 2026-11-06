import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        # Get full innerText of form container
        text = await pg.evaluate("""() => {
            let form = document.querySelector('form') || document.querySelector('main') || document.body;
            return form.innerText;
        }""")
        print("FULL FORM TEXT:\n" + "="*50)
        print(text)
        print("="*50)

if __name__ == '__main__':
    asyncio.run(main())

