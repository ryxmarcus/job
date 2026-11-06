import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BATCH_2 = [
    {
        'id': 'J093',
        'company': 'Thinkahead',
        'role': 'AI Platform Engineer',
        'url': 'https://jobs.lever.co/thinkahead/fa8521eb-285a-41d3-acfe-a0e46a3e5d4e/apply',
        'resume': 'DevOps_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J094',
        'company': 'Thinkahead',
        'role': 'Forward Deployed AI Security Engineer',
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
        'role': 'AI Software Engineer (DevOps)',
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

async def apply_job(context, job):
    print(f"\n==========================================")
    print(f"Opening & Filling [{job['id']}] {job['company']} - {job['role']}")
    print(f"URL: {job['url']}")

    page = await context.new_page()
    try:
        await page.goto(job['url'], wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(2)

        body = await page.inner_text('body')
        if 'position has been closed' in body.lower() or 'not found' in body.lower():
            print(f"[{job['id']}] Position is closed.")
            await page.close()
            return 'closed'

        pdf_path = os.path.abspath(os.path.join('job/resumes', job['resume']))
        if not os.path.exists(pdf_path):
            pdf_path = os.path.abspath('job/resumes/DevOps_Engineer_Rahul_Kumar.pdf')

        # 1. Resume
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(pdf_path)
            print("  Resume uploaded.")
            await asyncio.sleep(1.5)

        # 2. Basic Info
        fn = await page.query_selector('input[name="name"]')
        if fn:
            await fn.fill('Rahul Kumar')
        em = await page.query_selector('input[name="email"]')
        if em:
            await em.fill('rk58743k@gmail.com')
        ph = await page.query_selector('input[name="phone"]')
        if ph:
            await ph.fill('+91 7210476048')
        org = await page.query_selector('input[name="org"]')
        if org:
            await org.fill('Programming.com')
        li = await page.query_selector('input[name*="linkedin"], input[name*="urls[LinkedIn]"]')
        if li:
            await li.fill('https://linkedin.com/in/rahul-kumar-devops')
        gh = await page.query_selector('input[name*="github"], input[name*="urls[GitHub]"]')
        if gh:
            await gh.fill('https://github.com/rahulkumar')

        # 3. Location / Notice / CTC inputs
        inputs = await page.query_selector_all('input[type="text"], input:not([type])')
        for inp in inputs:
            lbl = (await inp.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
            val = await inp.input_value()
            if not val:
                if 'location' in lbl:
                    await inp.fill('Delhi NCR, India')
                elif 'notice' in lbl:
                    await inp.fill('30 Days (Serving notice)')
                elif 'experience' in lbl or 'years' in lbl:
                    await inp.fill('4.0 Years')
                elif 'salary' in lbl or 'compensation' in lbl or 'ctc' in lbl:
                    await inp.fill('Open / Not Disclosed')

        # 4. Radios
        radios = await page.query_selector_all('input[type="radio"]')
        for r in radios:
            val = (await r.get_attribute('value') or '').lower()
            lbl = (await r.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
            r_label = (await r.evaluate('e => e.closest("label") ? e.closest("label").innerText.toLowerCase() : ""') or '')
            
            if 'authorized' in lbl or 'eligible' in lbl or 'bachelor' in lbl or 'notice' in lbl:
                if val in ['yes', '1'] or 'yes' in r_label:
                    await r.click()
            elif 'sponsor' in lbl:
                if val in ['no', '0'] or 'no' in r_label:
                    await r.click()

        # 5. Select dropdowns
        selects = await page.query_selector_all('select')
        for s in selects:
            lbl = (await s.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
            opts = await s.query_selector_all('option')
            opt_texts = [(await o.text_content() or '').strip() for o in opts]
            
            if 'authorized' in lbl or 'india' in lbl:
                for o_txt in opt_texts:
                    if 'yes' in o_txt.lower():
                        await s.select_option(label=o_txt)
                        break
            elif 'sponsorship' in lbl or 'sponsor' in lbl:
                for o_txt in opt_texts:
                    if 'no' in o_txt.lower():
                        await s.select_option(label=o_txt)
                        break
            elif 'gender' in lbl:
                for o_txt in opt_texts:
                    if 'male' in o_txt.lower() and 'female' not in o_txt.lower():
                        await s.select_option(label=o_txt)
                        break

        print(f"[{job['id']}] Form completely populated in active tab.")
        return 'staged'

    except Exception as e:
        print(f"[{job['id']}] Error: {e}")
        return 'error'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        results = {}
        for job in BATCH_2:
            res = await apply_job(context, job)
            results[job['id']] = res
            await asyncio.sleep(2)
        print("\n--- Batch 2 Staging Results ---")
        for j_id, st in results.items():
            print(f"{j_id}: {st}")

asyncio.run(main())
