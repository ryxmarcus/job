import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        data = await pg.evaluate("""() => {
            if (window.__NEXT_DATA__) {
                return window.__NEXT_DATA__.props.pageProps.form || window.__NEXT_DATA__.props.pageProps;
            }
            return null;
        }""")
        if data:
            print("Keys in form props:", data.keys())
            # Find fields
            fields = data.get('fields', [])
            print(f"Total fields in form definition: {len(fields)}")
            for idx, f in enumerate(fields):
                print(f"[{idx}] Type: {f.get('type')} | Key: {f.get('key')} | Label: {f.get('label') or f.get('title')}")
                if 'rank' in str(f).lower():
                    print("   -> Ranking Field Details:", json.dumps(f, indent=2)[:500])

if __name__ == '__main__':
    asyncio.run(main())

