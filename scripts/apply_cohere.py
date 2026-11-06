import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        ctx = b.contexts[0]
        
        pg = None
        for page in ctx.pages:
            if 'coherehealth' in page.url:
                pg = page
                break
        
        if not pg:
            print("Opening Cohere Health page...")
            pg = await ctx.new_page()
            await pg.goto('https://job-boards.greenhouse.io/coherehealth/jobs/8037633003', wait_until='domcontentloaded')
            await asyncio.sleep(2)

        print("Filling Cohere Health application form...")
        await pg.fill('#first_name', 'Rahul')
        await pg.fill('#last_name', 'Kumar')
        
        pref = await pg.query_selector('#preferred_name')
        if pref:
            await pref.fill('Rahul')

        await pg.fill('#email', 'rk58743k@gmail.com')

        # Country selection if dropdown or input
        cntry = await pg.query_selector('#country')
        if cntry:
            await cntry.fill('India')
            await asyncio.sleep(1)
            await cntry.press('ArrowDown')
            await cntry.press('Enter')

        await pg.fill('#phone', '+91 7210476048')

        # Resume upload
        resume_path = os.path.abspath('job/resumes/Site_Reliability_Engineer_Rahul_Kumar.pdf')
        res_input = await pg.query_selector('input#resume')
        if res_input:
            print("Attaching resume...")
            await res_input.set_input_files(resume_path)
            await asyncio.sleep(2)

        # Questions
        q_answers = {
            '#question_33232091003': '4.0 years',
            '#question_33232122003': 'AWS (Amazon Web Services)',
            '#question_33232092003': 'EKS, EC2, S3, RDS, CloudWatch, Lambda, IAM, VPC, Route53, ALB/NLB, SQS',
            '#question_33232093003': 'Yes, defined 99.95% API availability & p99 < 200ms latency SLOs; led incident mitigation for EKS pod crashloop via automated canary rollbacks.',
            '#question_33232094003': 'Prometheus, Grafana, Datadog, AWS CloudWatch, ELK / OpenSearch',
            '#question_33232095003': '₹30 LPA (Open / In line with company benchmarks)',
            '#question_33180752003': '₹20 LPA',
            '#question_33232096003': '30 Days (Serving Notice Period)',
            '#question_33180741003': 'https://linkedin.com/in/rahul-kumar-devops',
            '#question_33180742003': 'https://github.com/rahulkumar',
            '#question_33180743003': 'Yes',
            '#question_33180744003': 'Company Career Page / LinkedIn',
            '#question_33180745003': 'No',
            '#question_33180746003': 'No',
            '#question_33180747003': 'N/A',
            '#question_33180748003': 'Rohini, New Delhi, Delhi 110085, India',
            '#question_33180749003': 'India (Delhi NCR)',
            '#question_33180750003': 'Yes, I understand and agree',
            '#question_33180751003': 'Rahul Kumar, 04/11/2026'
        }

        for sel, ans in q_answers.items():
            el = await pg.query_selector(sel)
            if el:
                await el.fill(ans)

        print("Cohere Health form successfully filled!")
        await asyncio.sleep(2)

        submit_btn = await pg.query_selector('button[type="submit"], #submit_app')
        if submit_btn:
            print("Submit button text:", await submit_btn.inner_text())
            captcha_iframe = await pg.query_selector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"]')
            if not captcha_iframe:
                print("Submitting Cohere Health application...")
                await submit_btn.click()
                await asyncio.sleep(5)
                print("Post-submission URL:", pg.url)
            else:
                print("CAPTCHA detected on page - kept open and staged for submission.")

if __name__ == '__main__':
    asyncio.run(main())

