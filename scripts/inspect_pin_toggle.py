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

        # Find toggle button for postalCode
        btn = await page.query_selector('button[id*="postalCode"][id*="toggle"]')
        if btn:
            print('Clicking toggle button for postal code...')
            await btn.click()
            await asyncio.sleep(2)

            # Let's inspect all elements that appeared in DOM
            listbox = await page.query_selector('[role="grid"], [role="listbox"], [id*="postalCode"][id*="listbox"]')
            if listbox:
                print('Found listbox container!')
                html = await listbox.evaluate('e => e.outerHTML')
                print('Listbox HTML:\n', html[:1500])
            else:
                print('Listbox container not found by selector, checking all popups...')
                popups = await page.query_selector_all('.cx-select__dropdown, .cx-select__list, [class*="dropdown"]')
                for pop in popups:
                    print('Popup class:', await pop.get_attribute('class'))
                    print('Popup text:', (await pop.text_content() or '').strip()[:200])

asyncio.run(main())

