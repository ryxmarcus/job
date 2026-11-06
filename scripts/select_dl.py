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

        # Click DL
        dl_opt = await page.query_selector('text="DL"')
        if dl_opt:
            print('Found DL option, clicking it!')
            await dl_opt.click()
            await asyncio.sleep(2)
        else:
            print('DL option not found directly, clicking by position...')

        # Now let's see Pin Code:
        pin = await page.query_selector('input[name="postalCode"]')
        if pin:
            print('Clicking Pin Code input...')
            await pin.click()
            await asyncio.sleep(1)

        await page.screenshot(path='job/amex_after_dl.png')
        print('Screenshot saved to job/amex_after_dl.png')

asyncio.run(main())

