import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        blocks = await pg.evaluate("""() => {
            return window.__NEXT_DATA__.props.pageProps.blocks || [];
        }""")
        print(f"Total blocks: {len(blocks)}")
        for idx, blk in enumerate(blocks):
            btype = blk.get('type')
            text = blk.get('text', '') or ''
            fields = blk.get('fields', [])
            if any(w in str(blk).lower() for w in ['rank', 'prioritise', 'prioritize', 'choice']):
                print(f"[{idx}] TYPE: {btype} | TEXT: {text[:80]}")
                if fields:
                    print("   FIELDS:", json.dumps(fields, indent=2)[:300])

if __name__ == '__main__':
    asyncio.run(main())

