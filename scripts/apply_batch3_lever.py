import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

LEVER_JOBS = [
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
    }
]

async def fill_lever_page(page, job):
    print(f"\n--- Filling {job['id']}: {job['company']} - {job['role']} ---")
    await page.goto(job['url'], wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(2)

    # Resume upload
    resume_path = os.path.abspath(os.path.join('job/resumes', job['resume']))
    file_input = await page.query_selector('input[type="file"]')
    if file_input:
        print(f"Uploading resume {job['resume']}...")
        await file_input.set_input_files(resume_path)
        await asyncio.sleep(2)

    # Basic inputs
    fields = [
        ('input[name="name"]', 'Rahul Kumar'),
        ('input[name="email"]', 'rk58743k@gmail.com'),
        ('input[name="phone"]', '+91 7210476048'),
        ('input[name="org"]', 'Programming.com'),
        ('input[name*="urls[LinkedIn]"], input[name*="linkedin"]', 'https://linkedin.com/in/rahul-kumar-devops'),
        ('input[name*="urls[GitHub]"], input[name*="github"]', 'https://github.com/rahulkumar'),
        ('input[name*="urls[Portfolio]"], input[name*="portfolio"]', 'https://github.com/rahulkumar'),
    ]

    for sel, val in fields:
        el = await page.query_selector(sel)
        if el:
            cur_val = await el.input_value()
            if not cur_val:
                await el.fill(val)

    # Location input if present
    loc = await page.query_selector('input[name="location"]')
    if loc:
        cur_val = await loc.input_value()
        if not cur_val:
            await loc.fill('Delhi, India')
            await asyncio.sleep(1)
            # select suggestion
            sugg = await page.query_selector('.tt-suggestion')
            if sugg:
                await sugg.click()
            else:
                await loc.press('ArrowDown')
                await loc.press('Enter')

    # Handle custom questions
    questions = await page.query_selector_all('.application-question')
    print(f"Total question blocks: {len(questions)}")
    for q in questions:
        q_text = (await q.inner_text()).lower()
        inp = await q.query_selector('input, textarea, select')
        if not inp:
            continue
        tag = await inp.evaluate('e => e.tagName')
        
        # Check notice period
        if 'notice' in q_text:
            if tag == 'INPUT' or tag == 'TEXTAREA':
                await inp.fill('30 Days (Serving notice)')
            elif tag == 'SELECT':
                # find 30 days or 1 month option
                opts = await inp.query_selector_all('option')
                for opt in opts:
                    otxt = (await opt.inner_text()).lower()
                    if '30' in otxt or '1 month' in otxt or 'immediate' in otxt:
                        val = await opt.get_attribute('value')
                        await inp.select_option(value=val)
                        break

        # Check compensation / salary / ctc
        elif any(w in q_text for w in ['ctc', 'salary', 'compensation', 'expectation']):
            if tag == 'INPUT' or tag == 'TEXTAREA':
                await inp.fill('Open / In accordance with company standards')
            elif tag == 'SELECT':
                opts = await inp.query_selector_all('option')
                for opt in opts:
                    otxt = (await opt.inner_text()).lower()
                    if 'open' in otxt or 'negotiable' in otxt:
                        val = await opt.get_attribute('value')
                        await inp.select_option(value=val)
                        break

        # Experience
        elif 'experience' in q_text or 'years' in q_text:
            if tag == 'INPUT':
                inp_type = await inp.get_attribute('type')
                if inp_type == 'radio':
                    radios = await q.query_selector_all('input[type="radio"]')
                    for r in radios:
                        lbl = await r.evaluate('e => e.parentElement.innerText')
                        if '4' in lbl or '3-5' in lbl or 'yes' in lbl.lower():
                            await r.check()
                            break
                else:
                    await inp.fill('4')
            elif tag == 'SELECT':
                opts = await inp.query_selector_all('option')
                for opt in opts:
                    otxt = (await opt.inner_text()).lower()
                    if '4' in otxt or '3-5' in otxt:
                        val = await opt.get_attribute('value')
                        await inp.select_option(value=val)
                        break

        # Authorization / Sponsorship
        elif any(w in q_text for w in ['authorized', 'legally', 'eligible to work']):
            # Usually Yes
            radios = await q.query_selector_all('input[type="radio"]')
            for r in radios:
                lbl = await r.evaluate('e => e.parentElement.innerText')
                if 'yes' in lbl.lower():
                    await r.check()
                    break

        elif any(w in q_text for w in ['sponsorship', 'require visa']):
            # Usually No
            radios = await q.query_selector_all('input[type="radio"]')
            for r in radios:
                lbl = await r.evaluate('e => e.parentElement.innerText')
                if 'no' in lbl.lower():
                    await r.check()
                    break

    await asyncio.sleep(2)
    # Check if there is a captcha
    captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
    print(f"[{job['id']}] CAPTCHA present: {bool(captcha)}")
    
    # Check submit button
    submit_btn = await page.query_selector('#btn-submit, button:has-text("Submit application")')
    if submit_btn and not captcha:
        print(f"[{job['id']}] Clicking Submit...")
        await submit_btn.click()
        await asyncio.sleep(5)
        print(f"[{job['id']}] Post-submit URL: {page.url}")
        if '/thanks' in page.url:
            print(f"[{job['id']}] SUCCESS! Application confirmed submitted!")
            return 'submitted'
        else:
            print(f"[{job['id']}] Submitted clicked, tab kept open for verification.")
            return 'clicked'
    else:
        print(f"[{job['id']}] Tab filled and staged.")
        return 'staged'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]

        for job in LEVER_JOBS:
            page = await context.new_page()
            try:
                res = await fill_lever_page(page, job)
                print(f"Result for {job['id']}: {res}")
            except Exception as e:
                print(f"Error on {job['id']}: {e}")

if __name__ == '__main__':
    asyncio.run(main())

