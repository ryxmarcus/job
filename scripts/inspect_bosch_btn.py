import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [p for p in b.contexts[0].pages if 'oneclick-ui' in p.url][0]
        btns = await pg.query_selector_all('button')
        for btn in btns:
            t = (await btn.inner_text()).strip().replace('\n', ' ')
            bid = await btn.get_attribute('id') or ''
            bclass = await btn.get_attribute('class') or ''
            print(f'button: text="{t}", id="{bid}", class="{bclass}"')

if __name__ == '__main__':
    asyncio.run(main())

