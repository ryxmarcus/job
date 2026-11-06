import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        
        # Find the Gemini ambassador tab
        pg = None
        for page in ctx.pages:
            if 'geministudentambassador' in page.url:
                pg = page
                break
                
        if not pg:
            print("Gemini Student Ambassador tab not found.")
            return

        print("Current tab URL:", pg.url)
        print("Current tab title:", await pg.title())

        # Check if still on Zscaler caution
        if 'zscaler' in (await pg.title()).lower():
            print("\nWaiting for you to click 'Continue' in the open browser tab...")
            for _ in range(30):
                await asyncio.sleep(2)
                t = await pg.title()
                if 'zscaler' not in t.lower():
                    print("Navigated past Zscaler! New title:", t)
                    break
            else:
                print("Still on Zscaler page. Please click 'Continue' on the browser tab.")
                return

        await asyncio.sleep(2)
        print("Inspecting loaded application form at:", pg.url)
        
        # Check inputs
        inputs = await pg.query_selector_all('input, select, textarea')
        print(f"Found {len(inputs)} form elements.")
        for inp in inputs:
            tag = await inp.evaluate('e => e.tagName')
            itype = await inp.get_attribute('type') or ''
            name = await inp.get_attribute('name') or ''
            id_attr = await inp.get_attribute('id') or ''
            placeholder = await inp.get_attribute('placeholder') or ''
            print(f"  [{tag}] id={id_attr}, name={name}, type={itype}, placeholder={placeholder}")

if __name__ == '__main__':
    asyncio.run(main())

