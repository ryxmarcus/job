import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        lingaro_page = None
        for p in context.pages:
            if 'lingarogroup' in p.url:
                lingaro_page = p
                break
        if not lingaro_page:
            return

        loc = await lingaro_page.query_selector('input[name="location"]')
        if loc:
            await loc.click()
            await loc.type('Delhi', delay=100)
            await asyncio.sleep(2)
            # Find suggestion
            sug = await lingaro_page.query_selector('.tt-suggestion, .location-suggestion, div[class*="suggestion"]')
            if sug:
                print('Found suggestion, clicking:', await sug.text_content())
                await sug.click()
            else:
                await lingaro_page.keyboard.press('ArrowDown')
                await asyncio.sleep(0.5)
                await lingaro_page.keyboard.press('Enter')
            await asyncio.sleep(1)

        print('Location val now:', await lingaro_page.eval_on_selector('input[name="location"]', 'e => e.value'))

        # Submit
        btn = await lingaro_page.query_selector('#btn-submit')
        if btn:
            print('Clicking Submit on Lingaro...')
            await btn.click()
            await asyncio.sleep(5)
            print('URL after submit:', lingaro_page.url)

asyncio.run(main())

