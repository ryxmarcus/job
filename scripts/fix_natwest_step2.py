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

        # 1. "How Did You Hear About Us?" button
        source_btn = await natwest_page.query_selector('[data-automation-id="source--source"]')
        if source_btn:
            print('Clicking source dropdown...')
            await source_btn.click()
            await asyncio.sleep(1)
            # Find options
            opts = await natwest_page.query_selector_all('[role="option"]')
            print(f'Source options: {len(opts)}')
            for o in opts:
                t = (await o.text_content() or '').strip()
                print('Opt:', t)
                if any(x in t.lower() for x in ['linkedin', 'job board', 'career site', 'internet']):
                    await o.click()
                    print('Selected source:', t)
                    break

        # 2. "Have you worked for NatWest Group..." -> Radio No
        # Look for radio buttons
        radios = await natwest_page.query_selector_all('input[type="radio"]')
        print(f'Total radios: {len(radios)}')
        for r in radios:
            r_val = await r.get_attribute('value')
            r_id = await r.get_attribute('id') or ''
            lbl = await natwest_page.query_selector(f'label[for="{r_id}"]')
            lbl_txt = (await lbl.text_content() or '').strip() if lbl else ''
            print(f'Radio id={r_id}, val={r_val}, label={lbl_txt}')
            if 'no' in lbl_txt.lower() or r_val == 'false':
                await r.click()
                print('Clicked No radio!')

        # 3. Title dropdown
        title_btn = await natwest_page.query_selector('[data-automation-id="name--legalName--title"]')
        if title_btn:
            txt = (await title_btn.text_content() or '').strip()
            if 'Select One' in txt:
                await title_btn.click()
                await asyncio.sleep(1)
                mr_opt = await natwest_page.query_selector('[role="option"]:has-text("Mr")')
                if mr_opt:
                    await mr_opt.click()
                    print('Selected Mr.')

        await asyncio.sleep(1)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Save:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Body preview:\n', txt[:600])

asyncio.run(main())

