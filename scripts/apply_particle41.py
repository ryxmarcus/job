import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        
        # Find Particle41 page
        pg = None
        for page in ctx.pages:
            if 'particle41' in page.url:
                pg = page
                break
        
        if not pg:
            print("Opening Particle41 page...")
            pg = await ctx.new_page()
            await pg.goto('https://job-boards.greenhouse.io/particle41llc/jobs/5018960008', wait_until='domcontentloaded')
            await asyncio.sleep(2)

        print("Filling Particle41 form...")
        # First name & Last name
        await pg.fill('#first_name', 'Rahul')
        await pg.fill('#last_name', 'Kumar')
        await pg.fill('#email', 'rk58743k@gmail.com')
        await pg.fill('#phone', '+91 7210476048')

        # Resume upload
        resume_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')
        res_input = await pg.query_selector('input#resume')
        if res_input:
            print("Attaching resume...")
            await res_input.set_input_files(resume_path)
            await asyncio.sleep(2)

        # LinkedIn Profile
        await pg.fill('#question_14008555008', 'https://linkedin.com/in/rahul-kumar-devops')

        # Website
        await pg.fill('#question_14008556008', 'https://github.com/rahulkumar')

        # Relevant work experience
        await pg.fill('#question_14008557008', '4.0 years')

        # Available to start
        await pg.fill('#question_14008558008', 'Within 30 Days (Serving Notice Period)')

        # Resigned from current employer
        await pg.fill('#question_14008559008', 'Yes, currently serving notice period')

        # Current CTC bracket (16L - 20L)
        cur_ctc = await pg.query_selector('#question_14008560008\\[\\]_25040021008')
        if cur_ctc:
            await cur_ctc.check()
        else:
            # fallback query by value
            chk = await pg.query_selector('input[value="25040021008"]')
            if chk:
                await chk.check()

        # Expected CTC bracket (26L or more)
        exp_ctc = await pg.query_selector('#question_14008561008\\[\\]_25040029008')
        if exp_ctc:
            await exp_ctc.check()
        else:
            chk2 = await pg.query_selector('input[value="25040029008"]')
            if chk2:
                await chk2.check()

        # Last working date
        await pg.fill('#question_14008562008', '04/12/2026')

        print("Particle41 form successfully filled!")
        await asyncio.sleep(2)

        # Check submit button
        submit_btn = await pg.query_selector('button[type="submit"], #submit_app')
        if submit_btn:
            print("Submit button found:", await submit_btn.inner_text())
            # Check captcha
            captcha_iframe = await pg.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"]')
            if not captcha_iframe:
                print("Submitting Particle41 application...")
                await submit_btn.click()
                await asyncio.sleep(5)
                print("Post-submission URL:", pg.url)
            else:
                print("CAPTCHA detected on page - kept open and staged for submission.")

if __name__ == '__main__':
    asyncio.run(main())

