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
            if 'careers.americanexpress.com' in p_elem.url:
                page = p_elem
                break
        if not page:
            print('AMEX page not found!')
            return

        err = await page.query_selector('#postalCode-59-error')
        if err:
            print('postalCode-59-error text:', await err.text_content())
        
        # Let's see what happens if we type in postalCode
        pin = await page.query_selector('#postalCode-59')
        if pin:
            print('Clicking and typing 110085...')
            await pin.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await pin.type('110085', delay=150)
            await asyncio.sleep(2)
            # Check if popup or options appear
            options = await page.query_selector_all('[role="option"], [role="row"]')
            print('Options after typing 110085:', len(options))
            for o in options[:5]:
                print('Opt:', await o.text_content())

asyncio.run(main())

