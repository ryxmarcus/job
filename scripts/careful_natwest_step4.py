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

        # If a popper is open, click "I acknowledge"
        ack = await natwest_page.query_selector('div:has-text("I acknowledge that these checks will take place"), li:has-text("I acknowledge")')
        if ack:
            print('Found open popper with I acknowledge, clicking it...')
            await ack.click()
            await asyncio.sleep(1)

        # Helper to click and select
        async def do_select(btn_id, keyword):
            btn = await natwest_page.query_selector(f'#{btn_id}')
            if not btn:
                print(f'Button {btn_id} not found!')
                return
            await btn.scroll_into_view_if_needed()
            await btn.click()
            await asyncio.sleep(1)
            opt = await natwest_page.query_selector(f'li[role="option"]:has-text("{keyword}"), div[data-automation-id="promptOption"]:has-text("{keyword}")')
            if opt:
                print(f'Selecting {keyword} for {btn_id}')
                await opt.click()
            else:
                print(f'Option {keyword} not found for {btn_id}')
            await asyncio.sleep(0.5)

        # Check each question button
        await do_select('primaryQuestionnaire--b34330ac1e16103b909b94d4a0a90000', 'I acknowledge')
        await do_select('primaryQuestionnaire--b34330ac1e16103b909b96a171bc0001', 'Yes')
        await do_select('primaryQuestionnaire--b34330ac1e16103b909b97d48e660002', 'No')
        await do_select('primaryQuestionnaire--b34330ac1e16103b909b986e29070002', 'No')
        await do_select('primaryQuestionnaire--eb095048c4d1103b90c6981581c80000', 'No')

        await asyncio.sleep(1)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue on Step 4...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 4:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Step 5 preview:\n', txt[:700])

asyncio.run(main())

