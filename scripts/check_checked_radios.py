import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'gemini' in page.url][0]

        radios = await pg.query_selector_all('input[type="radio"]')
        print(f"Total radios: {len(radios)}")
        checked_radios = []
        for idx, r in enumerate(radios):
            is_chk = await r.is_checked()
            rid = await r.get_attribute('id') or ''
            name = await r.get_attribute('name') or ''
            if is_chk:
                checked_radios.append((idx, name, rid))
        print("Checked radios:", checked_radios)

if __name__ == '__main__':
    asyncio.run(main())

