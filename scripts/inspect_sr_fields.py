import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = None
        for page in b.contexts[0].pages:
            if 'oneclick-ui' in page.url:
                pg = page
                break
        if not pg:
            print("SmartRecruiters oneclick-ui page not found")
            return
        
        inputs = await pg.query_selector_all('input')
        print(f"Total inputs on SmartRecruiters: {len(inputs)}")
        for inp in inputs:
            itype = await inp.get_attribute('type') or ''
            name = await inp.get_attribute('name') or ''
            id_attr = await inp.get_attribute('id') or ''
            aria = await inp.get_attribute('aria-label') or ''
            placeholder = await inp.get_attribute('placeholder') or ''
            print(f"type={itype}, id={id_attr}, name={name}, aria={aria}, placeholder={placeholder}")

if __name__ == '__main__':
    asyncio.run(main())

