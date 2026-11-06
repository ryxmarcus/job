import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        non_radios = await pg.query_selector_all('select, textarea, input:not([type="radio"])')
        print(f"Non-radio inputs count: {len(non_radios)}")
        for nr in non_radios:
            tag = await nr.evaluate('e => e.tagName')
            itype = await nr.get_attribute('type') or ''
            iid = await nr.get_attribute('id') or ''
            val = await nr.input_value() if tag == 'INPUT' else ''
            print(f"  [{tag}] type={itype}, id={iid}, val={val}")

        # Check ranking text
        body = await pg.inner_text('body')
        lines = [l.strip() for l in body.split('\n') if l.strip()]
        for i, l in enumerate(lines):
            if 'rank' in l.lower():
                print("\nRanking context:")
                for sub in lines[max(0, i-2):min(len(lines), i+15)]:
                    print("  >", sub)
                break

if __name__ == '__main__':
    asyncio.run(main())

