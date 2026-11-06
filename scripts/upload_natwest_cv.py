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
            print('Found file input in NatWest Workday!')
            await file_input.set_input_files(pdf_path)
            print('Set input file!')
            await asyncio.sleep(4)
            # Check Continue button
            cont_btn = await natwest_page.query_selector('button:has-text("Continue"), [data-automation-id="bottom-navigation-next-button"]')
            if cont_btn:
                print('Clicking Continue...')
                await cont_btn.click()
                await asyncio.sleep(6)
                print('URL after continue:', natwest_page.url)
                print('Page title:', await natwest_page.title())
                txt = await natwest_page.inner_text('body')
                print('NatWest step 2 excerpt:\n', txt[:600])

asyncio.run(main())

