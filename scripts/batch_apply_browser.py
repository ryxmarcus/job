import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LEVER_JOBS = [
    {
        'id': 'J022',
        'company': 'BrightEdge',
        'role': 'DevOps Engineer',
        'url': 'https://jobs.lever.co/brightedge/f0f18ff1-bf64-4a24-8521-1030cd05adcd/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J023',
        'company': 'Mactores',
        'role': 'AWS DevOps Engineer (Senior)',
        'url': 'https://jobs.lever.co/mactores/853c0359-3b02-4b50-b128-726dfc422a6c/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J026',
        'company': 'JumpCloud',
        'role': 'Site Reliability Engineer - India',
        'url': 'https://jobs.lever.co/jumpcloud/9bfc9bfb-15f0-4984-85dc-d1adc90a415c/apply',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J029',
        'company': 'Zimperium',
        'role': 'Site Reliability Engineer - India',
        'url': 'https://jobs.lever.co/zimperium/29aff3bb-b00f-457c-9ebb-70f3804c3fa6/apply',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J031',
        'company': 'Drivetrain',
        'role': 'Site Reliability Engineer - SRE',
        'url': 'https://jobs.lever.co/drivetrain/d1bc29ad-d0aa-47c8-8785-1094f279ccff/apply',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J093',
        'company': 'Thinkahead',
        'role': 'Senior Technical Consultant - AI Platform Engineer',
        'url': 'https://jobs.lever.co/thinkahead/fa8521eb-285a-41d3-acfe-a0e46a3e5d4e/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J094',
        'company': 'Thinkahead',
        'role': 'Senior Technical Consultant - Forward Deployed AI Security Engineer',
        'url': 'https://jobs.lever.co/thinkahead/a26ab4b0-87c1-4088-85c8-6ccb078684c4/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J095',
        'company': 'Lingarogroup',
        'role': 'Cloud DevOps Engineer',
        'url': 'https://jobs.lever.co/lingarogroup/b4aa26da-1f29-42d0-818a-93577800bc6b/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J096',
        'company': 'Zimperium',
        'role': 'AI Software Engineer (DevOps) - Bangalore',
        'url': 'https://jobs.lever.co/zimperium/5b35759a-d445-4fcb-b255-d719330af055/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J097',
        'company': 'Zimperium',
        'role': 'Lead DevOps Engineer (AI & GPU)',
        'url': 'https://jobs.lever.co/zimperium/f77ac05f-b87a-43ab-93d3-c2293b5400ef/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    }
]

async def apply_lever_job(context, job):
    print(f"\n==========================================")
    print(f"Processing [{job['id']}] {job['company']} - {job['role']}")
    print(f"URL: {job['url']}")

    page = await context.new_page()
    try:
        await page.goto(job['url'], wait_until='domcontentloaded', timeout=25000)
        await asyncio.sleep(2)

        body = await page.inner_text('body')
        if 'position has been closed' in body.lower() or 'not found' in body.lower():
            print(f"[{job['id']}] Position closed on Lever!")
            await page.close()
            return 'closed'

        # Resume path
        pdf_path = os.path.abspath(os.path.join('job/resumes', job['resume']))
        if not os.path.exists(pdf_path):
            pdf_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')

        # Upload resume
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(pdf_path)
            await asyncio.sleep(1.5)

        # Full name
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

        # Common Lever custom questions:
        # Notice Period
        np_input = await page.query_selector('input[name*="notice"], textarea[name*="notice"]')
        if np_input:
            await np_input.fill('30 Days (Serving notice)')

        # Current CTC / Expected CTC
        ctc_input = await page.query_selector('input[name*="salary"], input[name*="compensation"], input[name*="ctc"], textarea[name*="compensation"]')
        if ctc_input:
            await ctc_input.fill('Open / Not Disclosed')

        # Current Location
        loc_input = await page.query_selector('input[name="location"], input[name*="location"]')
        if loc_input:
            await loc_input.fill('Delhi NCR, India')

        # Work authorization / visa radio buttons:
        # Select "Yes" for authorized to work in India, "No" for requiring sponsorship
        auth_radios = await page.query_selector_all('input[type="radio"]')
        for r in auth_radios:
            val = (await r.get_attribute('value') or '').lower()
            lbl = (await r.evaluate('e => e.closest("label") ? e.closest("label").innerText : ""') or '').lower()
            if 'authorized' in lbl or 'eligible' in lbl or 'legal' in lbl:
                if val == 'yes' or 'yes' in lbl:
                    await r.click()
            elif 'sponsor' in lbl:
                if val == 'no' or 'no' in lbl:
                    await r.click()

        # Check for CAPTCHA
        captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
        submit_btn = await page.query_selector('#btn-submit, button:has-text("Submit Application")')

        if not captcha and submit_btn:
            print(f"[{job['id']}] No captcha detected, auto-submitting...")
            await submit_btn.click()
            await asyncio.sleep(5)
            new_body = await page.inner_text('body')
            if 'thank you' in new_body.lower() or 'submitted' in new_body.lower() or 'application received' in new_body.lower():
                print(f"[{job['id']}] Successfully submitted! Application confirmed.")
                await page.close()
                return 'submitted'
            else:
                print(f"[{job['id']}] Submitted, tab open for review.")
                return 'staged'
        else:
            print(f"[{job['id']}] Form fully pre-filled with resume, active in tab (CAPTCHA verification).")
            return 'staged'

    except Exception as e:
        print(f"[{job['id']}] Error: {e}")
        return 'error'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        results = {}
        for job in LEVER_JOBS[:5]: # Run first batch of 5
            res = await apply_lever_job(context, job)
            results[job['id']] = res
            await asyncio.sleep(2)
        print("\n--- Batch Run Results ---")
        for j_id, st in results.items():
            print(f"{j_id}: {st}")

asyncio.run(main())

