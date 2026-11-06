import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        txt = await pg.evaluate("""() => {
            let body = document.body.innerText;
            let start = body.indexOf('content creator on campus');
            let end = body.indexOf('A classmate publicly says');
            return body.substring(start, end + 100);
        }""")
        print("BETWEEN Q5 AND Q7:\n" + "="*50)
        print(txt)
        print("="*50)

if __name__ == '__main__':
    asyncio.run(main())

