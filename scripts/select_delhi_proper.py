import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = [page for page in b.contexts[0].pages if 'geministudentambassador' in page.url][0]
        
        # State input is #eac24c99-9b75-4011-960d-f8ae4f77d40d
        state_inp = await pg.query_selector('[id="eac24c99-9b75-4011-960d-f8ae4f77d40d"]')
        if state_inp:
            print("Clicking State input...")
            await state_inp.click()
            await asyncio.sleep(1)
            # Find options
            opts = await pg.query_selector_all('li, [role="option"], div[class*="item"]')
            print(f"State options found: {len(opts)}")
            for o in opts:
                t = (await o.inner_text()).strip()
                if t:
                    print(" State opt:", t)
                    if t.lower() == 'delhi':
                        await o.click()
                        print(" CLICKED DELHI!")
                        break

        await asyncio.sleep(1.5)
        # Now click on college input
        col_inp = await pg.query_selector('input[placeholder*="Search for your college"]')
        if col_inp:
            print("\nClicking College input after selecting Delhi...")
            await col_inp.click()
            await asyncio.sleep(1)
            col_opts = await pg.query_selector_all('li, [role="option"], div[class*="item"]')
            print(f"College options found for Delhi: {len(col_opts)}")
            for co in col_opts[:30]:
                txt = (await co.inner_text()).strip()
                if txt:
                    print("  College:", txt)

if __name__ == '__main__':
    asyncio.run(main())

