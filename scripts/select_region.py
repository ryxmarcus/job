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

        # Open toggle
        toggle = await page.query_selector('button[id*="region2"][id*="toggle"]')
        if toggle:
            await toggle.click()
            await asyncio.sleep(1)
            # Find all options
            options = await page.query_selector_all('[role="option"], li.oj-listbox-result')
            print(f'Total options: {len(options)}')
            for opt in options:
                txt = (await opt.text_content() or '').strip()
                if any(x in txt.lower() for x in ['delhi', 'haryana', 'ncr', 'dl', 'hr']):
                    print('Matching Option:', txt)
                    # Click it!
                    await opt.evaluate('e => e.click()')
                    print('Clicked matching option:', txt)
                    break
        
        await asyncio.sleep(1)
        print('Region after select:', await page.eval_on_selector('input[name="region2"]', 'e => e.value'))

asyncio.run(main())

