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

        print('At NatWest Step 4: Application Questions')
        # Print all form items / questions
        questions = await natwest_page.query_selector_all('fieldset, [data-automation-id*="question"], [data-automation-id*="formField"]')
        print(f'Total question containers: {len(questions)}')
        for q in questions:
            t = (await q.text_content() or '').strip()
            print('--- Q Block ---')
            print(t[:250])

asyncio.run(main())

