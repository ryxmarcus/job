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

        print('Selecting State/Region...')
        # Click toggle for state
        state_toggle = await page.query_selector('#region2-60-toggle-button, button[id*="region2"][id*="toggle"]')
        if state_toggle:
            await state_toggle.click()
            await asyncio.sleep(1)
            # Find Delhi option
            delhi_opt = await page.query_selector('li:has-text("Delhi"), [role="option"]:has-text("Delhi")')
            if delhi_opt:
                print('Found Delhi option in dropdown!')
                await delhi_opt.click()
            else:
                print('Delhi option not found, searching options:')
                opts = await page.query_selector_all('[role="option"], .oj-listbox-result')
                for o in opts[:10]:
                    print('Opt:', await o.text_content())
        
        # Postal code
        pin_input = await page.query_selector('input[name="postalCode"]')
        if pin_input:
            await pin_input.click()
            await pin_input.fill('110085')
            await page.keyboard.press('Tab')
            await asyncio.sleep(1)

        await asyncio.sleep(1)
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Next:', page.url)

asyncio.run(main())

