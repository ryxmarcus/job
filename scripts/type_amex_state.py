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

        # Let's set value and dispatch events via JS
        res = await page.evaluate('''() => {
            const regInput = document.querySelector('input[name="region2"]');
            if (regInput) {
                regInput.focus();
                regInput.value = 'Delhi';
                regInput.dispatchEvent(new Event('input', { bubbles: true }));
                regInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            const pinInput = document.querySelector('input[name="postalCode"]');
            if (pinInput) {
                pinInput.focus();
                pinInput.value = '110085';
                pinInput.dispatchEvent(new Event('input', { bubbles: true }));
                pinInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            return { reg: regInput ? regInput.value : null, pin: pinInput ? pinInput.value : null };
        }''')
        print('JS evaluate result:', res)
        await asyncio.sleep(1)

        # Now let's try typing into region2 to trigger Oracle JET suggestion
        reg_input = await page.query_selector('input[name="region2"]')
        if reg_input:
            await reg_input.click()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Backspace')
            await reg_input.type('Delhi', delay=100)
            await asyncio.sleep(1)
            await page.keyboard.press('ArrowDown')
            await asyncio.sleep(0.5)
            await page.keyboard.press('Enter')
            print('Typed Delhi and pressed Enter')

        await asyncio.sleep(1)
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            print('Clicking Next...')
            await next_btn.click()
            await asyncio.sleep(4)
            print('URL after Next:', page.url)

asyncio.run(main())

