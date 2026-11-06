import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        
        pg = await ctx.new_page()
        url = 'https://jobs.smartrecruiters.com/BoschGroup/744000155720139-devops-engineer-application-deployment-configuration-k8s-'
        print(f"Navigating to Bosch: {url}...")
        await pg.goto(url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)

        # Click "I'm interested" / "Apply" button on SmartRecruiters job description page
        apply_btn = await pg.query_selector('a:has-text("I\'m interested"), button:has-text("I\'m interested"), a:has-text("Apply")')
        if apply_btn:
            print("Found Apply / I'm interested button, clicking...")
            await apply_btn.click()
            await asyncio.sleep(3)

        print("Current URL:", pg.url)
        # Inspect inputs
        inputs = await pg.query_selector_all('input, textarea, select')
        print(f"Found {len(inputs)} inputs on SmartRecruiters form.")

        # Fill standard fields if present
        fn = await pg.query_selector('input[name="firstName"], #first-name-input')
        if fn: await fn.fill('Rahul')

        ln = await pg.query_selector('input[name="lastName"], #last-name-input')
        if ln: await ln.fill('Kumar')

        em = await pg.query_selector('input[name="email"], #email-input')
        if em: await em.fill('rk58743k@gmail.com')

        ph = await pg.query_selector('input[name="phoneNumber"], #phone-number-input')
        if ph: await ph.fill('+91 7210476048')

        # Resume upload
        resume_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')
        res_file = await pg.query_selector('input[type="file"]')
        if res_file:
            print("Attaching resume...")
            await res_file.set_input_files(resume_path)
            await asyncio.sleep(2)

        print("Bosch form checked and staged.")

if __name__ == '__main__':
    asyncio.run(main())

