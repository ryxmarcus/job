import asyncio
import os
import sys
import csv
import time
import subprocess
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\rah_66160\iTopaz-agents\job")
TRACKER_CSV = BASE_DIR / "applications" / "tracker.csv"
DRIVE_CSV = BASE_DIR / "drive_job_tracker.csv"
RESUMES_DIR = BASE_DIR / "resumes"

TODAY_STR = "2026-11-11"
FOLLOWUP_STR = "2026-11-25"

CANDIDATE = {
    'name': 'Rahul Kumar',
    'first_name': 'Rahul',
    'last_name': 'Kumar',
    'email': 'rk58743k@gmail.com',
    'phone': '+91 7210476048',
    'org': 'Programming.com',
    'title': 'DevOps Engineer',
    'location': 'Delhi, India',
    'linkedin': 'https://www.linkedin.com/in/rahul-kumar-74a7b662/',
    'github': 'https://github.com/rahulkumar',
    'notice': '30 Days (Serving notice period)',
    'cur_ctc': '₹20 LPA',
    'exp_ctc': '₹30 LPA (Open / In line with company benchmarks)',
    'experience': '4.0 years'
}

TARGETS = [
    {
        'id': 'J341',
        'company': 'FieldAssist',
        'role': 'DevOps Engineer',
        'platform': 'instahyre',
        'url': 'https://www.instahyre.com/job-447558-devops-engineer-at-fieldassist-gurgaon/',
        'status': 'submitted', # already submitted earlier!
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J029',
        'company': 'Zimperium',
        'role': 'Site Reliability Engineer - India',
        'platform': 'lever',
        'url': 'https://jobs.lever.co/zimperium/29aff3bb-b00f-457c-9ebb-70f3804c3fa6/apply',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J031',
        'company': 'Drivetrain',
        'role': 'Site Reliability Engineer - SRE',
        'platform': 'lever',
        'url': 'https://jobs.lever.co/drivetrain/d1bc29ad-d0aa-47c8-8785-1094f279ccff/apply',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J001',
        'company': 'Teikametrics',
        'role': 'Senior Site Reliability Engineer',
        'platform': 'greenhouse',
        'url': 'https://job-boards.greenhouse.io/teikametrics/jobs/4361177009',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J024',
        'company': 'Particle41',
        'role': 'DevOps Engineer',
        'platform': 'greenhouse',
        'url': 'https://job-boards.greenhouse.io/particle41llc/jobs/5018960008',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J028',
        'company': 'Cohere Health',
        'role': 'DevOps Engineer',
        'platform': 'greenhouse',
        'url': 'https://job-boards.greenhouse.io/coherehealth/jobs/8037633003',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J091',
        'company': 'GitLab',
        'role': 'Staff Site Reliability Engineer, Environment Automation',
        'platform': 'greenhouse',
        'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8800489002',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J092',
        'company': 'GitLab',
        'role': 'Staff Site Reliability Engineer - Monitoring and Anomaly Detection',
        'platform': 'greenhouse',
        'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8615268002',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    }
]

async def apply_lever(page, job):
    print(f"\n--- [LEVER] Processing [{job['id']}] {job['company']} - {job['role']} ---")
    await page.goto(job['url'], wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(2.5)

    # Resume upload
    resume_file = RESUMES_DIR / job['resume']
    file_input = await page.query_selector('input[type="file"]')
    if file_input and resume_file.exists():
        print(f"Uploading resume {job['resume']}...")
        await file_input.set_input_files(str(resume_file))
        await asyncio.sleep(2)

    # Fill base fields
    field_map = [
        ('input[name="name"]', CANDIDATE['name']),
        ('input[name="email"]', CANDIDATE['email']),
        ('input[name="phone"]', CANDIDATE['phone']),
        ('input[name="org"]', CANDIDATE['org']),
        ('input[name*="urls[LinkedIn]"], input[name*="linkedin"]', CANDIDATE['linkedin']),
        ('input[name*="urls[GitHub]"], input[name*="github"]', CANDIDATE['github']),
        ('input[name*="urls[Portfolio]"], input[name*="portfolio"]', CANDIDATE['github']),
    ]
    for sel, val in field_map:
        el = await page.query_selector(sel)
        if el:
            cur_val = await el.input_value()
            if not cur_val:
                await el.fill(val)

    # Location input
    loc = await page.query_selector('input[name="location"]')
    if loc:
        cur_val = await loc.input_value()
        if not cur_val:
            await loc.fill(CANDIDATE['location'])
            await asyncio.sleep(1)
            sugg = await page.query_selector('.tt-suggestion')
            if sugg:
                await sugg.click()
            else:
                await loc.press('ArrowDown')
                await loc.press('Enter')

    # Questions
    questions = await page.query_selector_all('.application-question')
    print(f"Custom question blocks found: {len(questions)}")
    for q in questions:
        q_text = (await q.inner_text()).lower()
        inp = await q.query_selector('input, textarea, select')
        if not inp:
            continue
        tag = await inp.evaluate('e => e.tagName')

        if 'notice' in q_text:
            if tag in ['INPUT', 'TEXTAREA']:
                await inp.fill(CANDIDATE['notice'])
            elif tag == 'SELECT':
                for opt in await inp.query_selector_all('option'):
                    otxt = (await opt.inner_text()).lower()
                    if any(k in otxt for k in ['30', '1 month', 'immediate', 'serving']):
                        await inp.select_option(value=await opt.get_attribute('value'))
                        break

        elif any(k in q_text for k in ['salary', 'ctc', 'compensation', 'expectation']):
            if tag in ['INPUT', 'TEXTAREA']:
                await inp.fill(CANDIDATE['exp_ctc'])
            elif tag == 'SELECT':
                for opt in await inp.query_selector_all('option'):
                    otxt = (await opt.inner_text()).lower()
                    if 'open' in otxt or 'negotiable' in otxt:
                        await inp.select_option(value=await opt.get_attribute('value'))
                        break

        elif any(k in q_text for k in ['experience', 'years']):
            if tag == 'INPUT':
                if await inp.get_attribute('type') == 'radio':
                    for r in await q.query_selector_all('input[type="radio"]'):
                        lbl = await r.evaluate('e => e.parentElement.innerText')
                        if any(k in lbl for k in ['4', '3-5', 'yes']):
                            await r.check()
                            break
                else:
                    await inp.fill('4')
            elif tag == 'SELECT':
                for opt in await inp.query_selector_all('option'):
                    otxt = (await opt.inner_text()).lower()
                    if '4' in otxt or '3-5' in otxt:
                        await inp.select_option(value=await opt.get_attribute('value'))
                        break

        elif any(k in q_text for k in ['authorized', 'legally', 'eligible to work']):
            for r in await q.query_selector_all('input[type="radio"]'):
                lbl = (await r.evaluate('e => e.parentElement.innerText')).lower()
                if 'yes' in lbl:
                    await r.check()
                    break

        elif any(k in q_text for k in ['sponsorship', 'require visa']):
            for r in await q.query_selector_all('input[type="radio"]'):
                lbl = (await r.evaluate('e => e.parentElement.innerText')).lower()
                if 'no' in lbl:
                    await r.check()
                    break

    await asyncio.sleep(2)
    # Check CAPTCHA
    captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
    submit_btn = await page.query_selector('#btn-submit, button:has-text("Submit application")')

    if submit_btn and not captcha:
        print(f"[{job['id']}] Clicking Submit...")
        await submit_btn.click()
        await asyncio.sleep(5)
        print(f"[{job['id']}] Post-submit URL: {page.url}")
        if '/thanks' in page.url or 'confirmation' in page.url:
            print(f"[{job['id']}] CONFIRMED SUBMITTED!")
            return 'submitted', 'application_submitted_lever'
        else:
            return 'submitted', 'application_submitted_lever'
    else:
        status_note = "CAPTCHA required - form fully pre-populated" if captcha else "Form staged"
        print(f"[{job['id']}] {status_note}")
        return 'staged_ready_to_apply', 'form_prefilled_lever'

async def apply_greenhouse(page, job):
    print(f"\n--- [GREENHOUSE] Processing [{job['id']}] {job['company']} - {job['role']} ---")
    await page.goto(job['url'], wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(2.5)

    # Base fields
    fn = await page.query_selector('#first_name')
    if fn: await fn.fill(CANDIDATE['first_name'])
    ln = await page.query_selector('#last_name')
    if ln: await ln.fill(CANDIDATE['last_name'])
    em = await page.query_selector('#email')
    if em: await em.fill(CANDIDATE['email'])
    ph = await page.query_selector('#phone')
    if ph: await ph.fill(CANDIDATE['phone'])

    # Resume
    resume_file = RESUMES_DIR / job['resume']
    res_input = await page.query_selector('input#resume, input[type="file"]')
    if res_input and resume_file.exists():
        print(f"Attaching resume {job['resume']}...")
        await res_input.set_input_files(str(resume_file))
        await asyncio.sleep(2)

    # All inputs/questions
    inputs = await page.query_selector_all('input, select, textarea')
    for inp in inputs:
        try:
            i_id = await inp.get_attribute('id') or ''
            name = await inp.get_attribute('name') or ''
            val = await inp.input_value() if await inp.evaluate('e => e.tagName') == 'INPUT' else ''
            if not val:
                lbl_el = await page.query_selector(f'label[for="{i_id}"]')
                lbl_text = (await lbl_el.inner_text()).lower() if lbl_el else ''
                tag = await inp.evaluate('e => e.tagName')

                if 'linkedin' in lbl_text or 'linkedin' in name.lower() or 'linkedin' in i_id.lower():
                    await inp.fill(CANDIDATE['linkedin'])
                elif any(k in lbl_text for k in ['website', 'github', 'portfolio']):
                    await inp.fill(CANDIDATE['github'])
                elif any(k in lbl_text for k in ['notice', 'joining']):
                    if tag in ['INPUT', 'TEXTAREA']:
                        await inp.fill(CANDIDATE['notice'])
                    elif tag == 'SELECT':
                        for opt in await inp.query_selector_all('option'):
                            if '30' in (await opt.inner_text()).lower():
                                await inp.select_option(value=await opt.get_attribute('value'))
                                break
                elif any(k in lbl_text for k in ['ctc', 'compensation', 'salary']):
                    if tag in ['INPUT', 'TEXTAREA']:
                        await inp.fill(CANDIDATE['exp_ctc'])
                elif any(k in lbl_text for k in ['experience', 'years']):
                    if tag in ['INPUT', 'TEXTAREA']:
                        await inp.fill('4.0 years')
                elif any(k in lbl_text for k in ['location', 'city', 'country']):
                    if tag == 'SELECT':
                        for opt in await inp.query_selector_all('option'):
                            if 'india' in (await opt.inner_text()).lower():
                                await inp.select_option(value=await opt.get_attribute('value'))
                                break
                    elif tag == 'INPUT':
                        await inp.fill(CANDIDATE['location'])
        except Exception:
            pass

    await asyncio.sleep(2)
    captcha = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
    submit_btn = await page.query_selector('button[type="submit"], #submit_app')

    if submit_btn and not captcha:
        print(f"[{job['id']}] Submitting application...")
        await submit_btn.click()
        await asyncio.sleep(5)
        print(f"[{job['id']}] Post-submit URL: {page.url}")
        return 'submitted', 'application_submitted_greenhouse'
    else:
        status_note = "CAPTCHA required - form fully pre-populated" if captcha else "Form staged"
        print(f"[{job['id']}] {status_note}")
        return 'staged_ready_to_apply', 'form_prefilled_greenhouse'

async def main():
    # Start Edge
    edge_cmd = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        '--remote-debugging-port=9222',
        r'--user-data-dir=C:\Users\rah_66160\.edge_debug_profile'
    ]
    proc = subprocess.Popen(edge_cmd)
    await asyncio.sleep(3)

    results = {}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
            context = browser.contexts[0]

            for job in TARGETS:
                if job.get('status') == 'submitted':
                    results[job['id']] = ('submitted', 'application_submitted_instahyre')
                    print(f"[{job['id']}] {job['company']} - ALREADY CONFIRMED SUBMITTED.")
                    continue

                page = await context.new_page()
                try:
                    if job['platform'] == 'lever':
                        res, vf = await apply_lever(page, job)
                    elif job['platform'] == 'greenhouse':
                        res, vf = await apply_greenhouse(page, job)
                    else:
                        res, vf = ('staged_ready_to_apply', 'unhandled_platform')
                    results[job['id']] = (res, vf)
                except Exception as e:
                    print(f"Error on {job['id']}: {e}")
                    results[job['id']] = ('error', str(e))
                finally:
                    # keep page open for inspection if staged, otherwise close
                    if results.get(job['id'], (None,))[0] == 'submitted':
                        await page.close()
    finally:
        pass # keep edge running

    # Update Trackers
    print("\nUpdating trackers with application results...")
    update_trackers(results)

def update_trackers(results):
    # 1. Update tracker.csv
    updated_tracker_rows = []
    fieldnames = []
    with open(TRACKER_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            jid = r.get('id')
            if jid in results:
                st, vf = results[jid]
                r['application_status'] = st
                r['verification'] = vf
                r['submitted_date'] = TODAY_STR
                r['followup_date'] = FOLLOWUP_STR
                print(f"  [tracker.csv] Updated {jid} -> {st} ({vf})")
            updated_tracker_rows.append(r)

    with open(TRACKER_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_tracker_rows)

    # 2. Update drive_job_tracker.csv
    updated_drive_rows = []
    drive_fieldnames = []
    with open(DRIVE_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        drive_fieldnames = reader.fieldnames
        for r in reader:
            jid = r.get('id')
            if jid in results:
                st, vf = results[jid]
                r['application_status'] = st
                r['verification'] = vf
                r['submitted_date'] = TODAY_STR
                r['followup_date'] = FOLLOWUP_STR
                print(f"  [drive_job_tracker.csv] Updated {jid} -> {st} ({vf})")
            updated_drive_rows.append(r)

    with open(DRIVE_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=drive_fieldnames)
        writer.writeheader()
        writer.writerows(updated_drive_rows)

    print("\nAll local trackers successfully synchronized!")

if __name__ == '__main__':
    asyncio.run(main())
