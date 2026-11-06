import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        natwest_page = None
        for p_elem in context.pages:
            if 'rbs.wd3.myworkdayjobs.com' in p_elem.url:
                natwest_page = p_elem
                break
        if not natwest_page:
            print('NatWest page not found!')
            return

        print('At Step 6: Review. Finding Submit button...')
        submit_btn = await natwest_page.query_selector('button[data-automation-id="bottom-navigation-next-button"]:has-text("Submit"), button:has-text("Submit")')
        if submit_btn:
            print('Clicking NatWest Workday Submit button!')
            await submit_btn.click()
            await asyncio.sleep(8)
            print('Final URL after Submit:', natwest_page.url)
            print('Final Title:', await natwest_page.title())
            body_txt = await natwest_page.inner_text('body')
            print('Confirmation snippet:\n', body_txt[:800])
        else:
            print('Submit button not found!')

asyncio.run(main())

