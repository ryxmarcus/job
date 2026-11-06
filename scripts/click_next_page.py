import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]

        # 1. Select Delhi for State
        state_inp = await pg.query_selector('[id="eac24c99-9b75-4011-960d-f8ae4f77d40d"]')
        if state_inp:
            print("Selecting State: Delhi...")
            await state_inp.click()
            await asyncio.sleep(0.5)
            opts = await pg.query_selector_all('li, [role="option"], div[class*="item"]')
            for o in opts:
                t = (await o.inner_text()).strip()
                if t.lower() == 'delhi':
                    await o.click()
                    print("Selected Delhi successfully!")
                    break

        await asyncio.sleep(1)

        # 2. Click Next button
        next_btn = await pg.query_selector('button:has-text("Next")')
        if next_btn:
            print("Clicking Next button to switch to next page...")
            await next_btn.click()
            await asyncio.sleep(3)
            
            print("\n=== PAGE 2 LOADED ===")
            print("Title:", await pg.title())
            body = await pg.inner_text('body')
            print(body[:2000])

if __name__ == '__main__':
    asyncio.run(main())

