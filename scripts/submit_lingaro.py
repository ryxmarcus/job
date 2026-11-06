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
            print('Lingaro page not found!')
            return

        loc = await lingaro_page.query_selector('input[name="location"]')
        if loc:
            print('Typing location...')
            await loc.click()
            await loc.fill('Delhi, IND')
            await asyncio.sleep(1)
            await lingaro_page.keyboard.press('ArrowDown')
            await asyncio.sleep(0.5)
            await lingaro_page.keyboard.press('Enter')
            await asyncio.sleep(1)

        # Also set selectedLocation via JS if needed
        await lingaro_page.evaluate('''() => {
            const selLoc = document.querySelector('input[name="selectedLocation"]');
            if (selLoc) {
                selLoc.value = '{"name":"Delhi, IND","address":{"city":"Delhi","country":{"code":"IN","description":""},"CountryCode":"IN"}}';
            }
        }''')

        # Click submit
        btn = await lingaro_page.query_selector('#btn-submit, button:has-text("Submit application")')
        if btn:
            print('Clicking Submit on Lingaro...')
            await btn.click()
            await asyncio.sleep(6)
            print('URL after submit:', lingaro_page.url)
            txt = await lingaro_page.inner_text('body')
            if 'thanks' in lingaro_page.url or any(k in txt.lower() for k in ['thank you', 'received', 'submitted']):
                print('LINGARO SUBMISSION SUCCESSFUL!')

asyncio.run(main())

