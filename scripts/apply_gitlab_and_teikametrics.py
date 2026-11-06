import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TARGETS = [
    {
        'id': 'J001',
        'company': 'Teikametrics',
        'role': 'Senior Site Reliability Engineer',
        'url': 'https://job-boards.greenhouse.io/teikametrics/jobs/4361177009',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J091',
        'company': 'GitLab',
        'role': 'Staff Site Reliability Engineer, Environment Automation',
        'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8800489002',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    },
    {
        'id': 'J092',
        'company': 'GitLab',
        'role': 'Staff Site Reliability Engineer - Monitoring',
        'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8615268002',
        'resume': 'Site_Reliability_Engineer_Rahul_Kumar.pdf'
    }
]

async def process_job(ctx, item):
    print(f"\n==========================================")
    print(f"Processing [{item['id']}] {item['company']} - {item['role']}")
    print(f"URL: {item['url']}")
    
    pg = await ctx.new_page()
    await pg.goto(item['url'], wait_until='domcontentloaded', timeout=30000)
    await asyncio.sleep(2)

    # Basic fields
    fn = await pg.query_selector('#first_name')
    if fn: await fn.fill('Rahul')
    
    ln = await pg.query_selector('#last_name')
    if ln: await ln.fill('Kumar')

    em = await pg.query_selector('#email')
    if em: await em.fill('rk58743k@gmail.com')

    ph = await pg.query_selector('#phone')
    if ph: await ph.fill('+91 7210476048')

    # Resume
    resume_path = os.path.abspath(os.path.join('job/resumes', item['resume']))
    res_input = await pg.query_selector('input#resume, input[type="file"]')
    if res_input:
        print("Attaching resume...")
        await res_input.set_input_files(resume_path)
        await asyncio.sleep(2)

    # Inspect all inputs and questions
    inputs = await pg.query_selector_all('input, select, textarea')
    print(f"Total inputs on page: {len(inputs)}")
    for inp in inputs:
        i_id = await inp.get_attribute('id') or ''
        name = await inp.get_attribute('name') or ''
        val = await inp.input_value() if await inp.evaluate('e => e.tagName') == 'INPUT' else ''
        if not val:
            # Check label
            lbl_el = await pg.query_selector(f'label[for="{i_id}"]')
            lbl_text = (await lbl_el.inner_text()).lower() if lbl_el else ''
            
            if 'linkedin' in lbl_text or 'linkedin' in name.lower() or 'linkedin' in i_id.lower():
                await inp.fill('https://linkedin.com/in/rahul-kumar-devops')
            elif 'website' in lbl_text or 'github' in lbl_text or 'portfolio' in lbl_text:
                await inp.fill('https://github.com/rahulkumar')
            elif any(w in lbl_text for w in ['notice', 'joining']):
                await inp.fill('30 Days (Serving Notice Period)')
            elif any(w in lbl_text for w in ['ctc', 'compensation', 'salary']):
                await inp.fill('₹30 LPA (Open / In line with company benchmarks)')
            elif 'experience' in lbl_text or 'years' in lbl_text:
                await inp.fill('4.0 years')
            elif 'location' in lbl_text or 'city' in lbl_text or 'country' in lbl_text:
                if await inp.evaluate('e => e.tagName') == 'SELECT':
                    opts = await inp.query_selector_all('option')
                    for o in opts:
                        if 'india' in (await o.inner_text()).lower():
                            await inp.select_option(value=await o.get_attribute('value'))
                            break
                else:
                    await inp.fill('Delhi, India')

    await asyncio.sleep(2)
    # Check submit button & captcha
    submit_btn = await pg.query_selector('button[type="submit"], #submit_app')
    captcha = await pg.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], iframe[src*="turnstile"]')
    print(f"[{item['id']}] Submit button: {bool(submit_btn)} | CAPTCHA: {bool(captcha)}")
    if submit_btn and not captcha:
        print(f"[{item['id']}] Submitting application...")
        await submit_btn.click()
        await asyncio.sleep(5)
        print(f"[{item['id']}] Post-submit URL: {pg.url}")
    else:
        print(f"[{item['id']}] Form completely populated and staged in tab.")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        for job in TARGETS:
            try:
                await process_job(ctx, job)
            except Exception as e:
                print(f"Error on {job['id']}: {e}")

if __name__ == '__main__':
    asyncio.run(main())

