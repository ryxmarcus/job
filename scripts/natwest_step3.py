import asyncio
import os
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

        pdf_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')
        print('Target resume path:', pdf_path)
        
        file_input = await natwest_page.query_selector('input[type="file"]')
        if file_input:
            print('Found file input in NatWest Step 3!')
            await file_input.set_input_files(pdf_path)
            print('Uploaded resume!')
            await asyncio.sleep(4)

        # Click Save and Continue
        save_btn = await natwest_page.query_selector('[data-automation-id="bottom-navigation-next-button"], button:has-text("Save and Continue")')
        if save_btn:
            print('Clicking Save and Continue on Step 3...')
            await save_btn.click()
            await asyncio.sleep(6)
            print('URL after Step 3:', natwest_page.url)
            txt = await natwest_page.inner_text('body')
            print('Step 4 excerpt:\n', txt[:700])

asyncio.run(main())

