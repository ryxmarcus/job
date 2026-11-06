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

        src_btn = await natwest_page.query_selector('#source--source')
        if src_btn:
            print('Clicking #source--source...')
            await src_btn.click()
            await asyncio.sleep(1)
            # Find all options visible right now
            opts = await natwest_page.query_selector_all('li[role="option"]')
            print(f'Total visible options: {len(opts)}')
            for o in opts:
                t = (await o.text_content() or '').strip()
                print('Source Opt:', t)
                if any(k in t.lower() for k in ['career', 'job board', 'linkedin', 'internet', 'other']):
                    print('Selecting matching source:', t)
                    await o.click()
                    break

        await asyncio.sleep(2)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 2 save:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Body excerpt after step 2:\n', txt[:600])

asyncio.run(main())

