import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        # Open in a dedicated tab
        page = await context.new_page()
        url = 'https://jobs.lever.co/brightedge/f0f18ff1-bf64-4a24-8521-1030cd05adcd/apply'
        print(f'Navigating to {url}...')
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)
        print('Title:', await page.title())

        # Check if posting is active
        body = await page.inner_text('body')
        if 'this position has been closed' in body.lower() or 'not found' in body.lower():
            print('Posting closed!')
            await page.close()
            return

        pdf_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')

        # Upload resume
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            print('Uploading resume...')
            await file_input.set_input_files(pdf_path)
            await asyncio.sleep(2)

        # Full Name
        fn = await page.query_selector('input[name="name"]')
        if fn:
            await fn.fill('Rahul Kumar')

        # Email
        em = await page.query_selector('input[name="email"]')
        if em:
            await em.fill('rk58743k@gmail.com')

        # Phone
        ph = await page.query_selector('input[name="phone"]')
        if ph:
            await ph.fill('+91 7210476048')

        # Current Company
        org = await page.query_selector('input[name="org"]')
        if org:
            await org.fill('Programming.com')

        # LinkedIn
        li = await page.query_selector('input[name*="linkedin"], input[name*="urls[LinkedIn]"]')
        if li:
            await li.fill('https://linkedin.com/in/rahul-kumar-devops')

        # GitHub
        gh = await page.query_selector('input[name*="github"], input[name*="urls[GitHub]"]')
        if gh:
            await gh.fill('https://github.com/rahulkumar')

        # Other inputs / questions
        other_inputs = await page.query_selector_all('.application-question input, .application-question select, .application-question textarea')
        print(f'Additional question inputs: {len(other_inputs)}')
        for inp in other_inputs:
            t = await inp.evaluate('e => e.tagName')
            n = await inp.get_attribute('name') or ''
            val = await inp.input_value() if t == 'INPUT' else ''
            print(f'  Input: tag={t}, name={n}, val="{val}"')

        # Check Submit button
        submit_btn = await page.query_selector('#btn-submit, button:has-text("Submit Application")')
        if submit_btn:
            print('Submit button found!')
            # Check if captcha exists
            has_captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
            print('Has CAPTCHA:', bool(has_captcha))
            if not has_captcha:
                print('Submitting application...')
                await submit_btn.click()
                await asyncio.sleep(5)
                print('URL after submit:', page.url)
                print('Title after submit:', await page.title())
                txt = await page.inner_text('body')
                print('Result text snippet:\n', txt[:400])
            else:
                print('Page has CAPTCHA, staged in open tab for user confirmation.')
        else:
            print('Submit button not found!')

asyncio.run(main())

