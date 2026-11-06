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

        # Let's inspect the region2 input container
        info = await page.evaluate('''() => {
            const input = document.querySelector('input[name="region2"]');
            const parent = input ? input.closest('.oj-combobox-one, oj-combobox-one, .oj-form-control') : null;
            return {
                inputId: input ? input.id : null,
                parentTag: parent ? parent.tagName : null,
                parentHtml: parent ? parent.outerHTML.slice(0, 300) : null
            };
        }''')
        print('Info:', info)

        # Let's see what happens if we type 'DL' or 'Delhi' into region2 and blur
        await page.evaluate('''() => {
            const input = document.querySelector('input[name="region2"]');
            input.value = 'DL';
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }''')
        
        # Also let's set postal code
        await page.evaluate('''() => {
            const pin = document.querySelector('input[name="postalCode"]');
            if (pin) {
                pin.value = '110085';
                pin.dispatchEvent(new Event('input', { bubbles: true }));
                pin.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }''')
        await asyncio.sleep(1)

        # Let's check value of region2 and postalCode
        reg_val = await page.eval_on_selector('input[name="region2"]', 'e => e.value')
        pin_val = await page.eval_on_selector('input[name="postalCode"]', 'e => e.value')
        print('reg_val:', reg_val, 'pin_val:', pin_val)

        # Click Next
        next_btn = await page.query_selector('button:has-text("Next")')
        if next_btn:
            await next_btn.click()
            await asyncio.sleep(3)
            print('URL after Next:', page.url)

asyncio.run(main())

