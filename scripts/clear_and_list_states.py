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

        inp = await page.query_selector('input[name="region2"]')
        if inp:
            await inp.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await asyncio.sleep(1)

        toggle = await page.query_selector('button[id*="region2"][id*="toggle"]')
        if toggle:
            await toggle.click()
            await asyncio.sleep(2)

        listbox = await page.query_selector('[id*="region2"][id*="listbox"]')
        if listbox:
            txt = await listbox.inner_text()
            print('Listbox text after clear:\n', txt[:500])

asyncio.run(main())

