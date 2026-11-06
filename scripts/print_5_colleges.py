import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        col_inp = await pg.query_selector('input[placeholder*="Search for your college"]')
        await col_inp.click()
        await asyncio.sleep(1)
        opts = await pg.query_selector_all('li, [role="option"], div[class*="item"]')
        for idx, o in enumerate(opts):
            t = (await o.inner_text()).strip()
            if t:
                print(f"[{idx}] {t}")

if __name__ == '__main__':
    asyncio.run(main())

