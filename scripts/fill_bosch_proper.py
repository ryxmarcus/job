import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        pg = None
        for page in b.contexts[0].pages:
            if 'oneclick-ui' in page.url:
                pg = page
                break
        if not pg:
            print("SmartRecruiters page not found")
            return

        print("Filling Bosch SmartRecruiters form...")
        # Resume upload
        resume_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')
        res_file = await pg.query_selector('input[type="file"]')
        if res_file:
            print("Attaching resume...")
            await res_file.set_input_files(resume_path)
            await asyncio.sleep(2)

        # Name & Contact
        await pg.fill('input#first-name-input', 'Rahul')
        await pg.fill('input#last-name-input', 'Kumar')
        await pg.fill('input#email-input', 'rk58743k@gmail.com')
        
        conf_em = await pg.query_selector('input#confirm-email-input')
        if conf_em:
            await conf_em.fill('rk58743k@gmail.com')

        ph = await pg.query_selector('input[type="tel"]')
        if ph:
            await ph.fill('+91 7210476048')

        li = await pg.query_selector('input#linkedin-input')
        if li:
            await li.fill('https://linkedin.com/in/rahul-kumar-devops')

        web = await pg.query_selector('input#website-input')
        if web:
            await web.fill('https://github.com/rahulkumar')

        print("Bosch form successfully filled!")
        await asyncio.sleep(2)

        # Look for Next / Submit button
        next_btn = await pg.query_selector('button:has-text("Next"), button:has-text("Submit"), button#c-form-submit')
        if next_btn:
            print("Next/Submit button found:", await next_btn.inner_text())
            await next_btn.click()
            await asyncio.sleep(3)
            print("Post click URL:", pg.url)

if __name__ == '__main__':
    asyncio.run(main())

