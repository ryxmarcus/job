import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def select_option(page, btn_id, target_val):
    btn = await page.query_selector(f'#{btn_id}')
    if not btn:
        print(f'Button {btn_id} not found!')
        return
    print(f'Clicking button {btn_id}...')
    await btn.click()
    await asyncio.sleep(1)
    # Find options
    opts = await page.query_selector_all('li[role="option"]')
    for opt in opts:
        txt = (await opt.text_content() or '').strip()
        if target_val.lower() in txt.lower():
            print(f'Selecting {txt} for {btn_id}')
            await opt.click()
            await asyncio.sleep(0.5)
            return
    print(f'Option {target_val} not found among {len(opts)} options for {btn_id}')

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

        buttons = [
            ('primaryQuestionnaire--b34330ac1e16103b909b94d4a0a90000', 'Yes'), # Acknowledge / confirm
            ('primaryQuestionnaire--b34330ac1e16103b909b96a171bc0001', 'Yes'), # Indian nationality
            ('primaryQuestionnaire--b34330ac1e16103b909b97d48e660002', 'No'),  # Redundant 12m
            ('primaryQuestionnaire--b34330ac1e16103b909b986e29070002', 'No'),  # Misconduct
            ('primaryQuestionnaire--eb095048c4d1103b90c6981581c80000', 'No'),  # Adjustments
        ]

        for b_id, val in buttons:
            await select_option(natwest_page, b_id, val)

        await asyncio.sleep(2)
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue on Step 4...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 4:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Step 5 preview:\n', txt[:700])

asyncio.run(main())

