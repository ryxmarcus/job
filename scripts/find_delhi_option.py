import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = None
        for p_elem in context.pages:
            if 'job/26015724/apply' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX apply page not found!')
            return

        # Let's inspect the region2 input element and its toggle button
        reg_btn = await page.query_selector('button[id*="region2"][id*="toggle"]')
        if reg_btn:
            print('Clicking region toggle...')
            await reg_btn.click()
            await asyncio.sleep(1)

        # Let's see what options are returned by typing 'Del' into region2
        reg_input = await page.query_selector('input[name="region2"]')
        if reg_input:
            await reg_input.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await reg_input.type('Del', delay=100)
            await asyncio.sleep(2)
            # Find all options visible
            opts = await page.query_selector_all('[role="row"], [role="option"], .cx-select__list-item, div[class*="item"]')
            print(f'Options found after typing Del: {len(opts)}')
            for o in opts:
                t = (await o.text_content() or '').strip()
                if 'delhi' in t.lower() or 'dl' in t.lower():
                    print('Found Delhi option:', t)
                    await o.click()
                    print('Clicked Delhi option!')
                    break

        await asyncio.sleep(1)
        r = await page.eval_on_selector('input[name="region2"]', 'e => e.value')
        print('Region is now:', r)

asyncio.run(main())

