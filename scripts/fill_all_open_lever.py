import asyncio
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ANSWERS = {
    'relevant certifications': 'AWS Certified DevOps Engineer - Professional (DOP-C02) & AWS Certified Data Engineer (DEA-C01). Extensive production experience in Kubernetes, Docker, Terraform, and automated CI/CD release engineering.',
    'challenging technical issue': 'Resolved a critical Kubernetes production cluster OOM crash during peak ETL ingestion by profiling container memory leakages, fine-tuning cgroup v2 memory limits, and configuring horizontal pod autoscaling with custom Prometheus metrics.',
    'security and reliability': 'By embedding automated vulnerability scanning (Trivy/SonarQube), enforcing least-privilege IAM policies, managing encrypted secrets in AWS Secrets Manager, and implementing automated canary deployments with health telemetry rollback.',
    'setting up continuous integration': 'Yes, architected and automated enterprise CI/CD pipelines in Jenkins and GitHub Actions with automated unit tests, container builds, Docker registry pushes, and ArgoCD Helm GitOps rollouts.',
    'collaborate with cross-functional': 'Partnered with software development, QA, and security teams to implement automated staging environments on AWS EKS, reducing deployment cycle lead time from days to 15 minutes.',
    'motivated you to pursue a career in devops': 'Passionate about bridging software engineering and systems reliability. The most rewarding aspect is eliminating manual operational toil and enabling engineers to ship resilient production software fearlessly.',
    'stay updated with the latest trends': 'Regularly follow CNCF announcements, AWS architecture blogs, GitHub open source releases, and participate in Cloud Native engineering forums.',
    'experience with amazon web services': '4.0 verified years of production AWS engineering across EKS, EC2, S3, RDS, IAM, CloudWatch, Lambda, CloudFront, VPC networking, and Infrastructure as Code with Terraform.',
    'maintenance of sql': 'Managed PostgreSQL and MySQL performance optimizations, vacuuming schedules, read replica scaling, query index tuning, and automated zero-downtime database schema migrations via Liquibase.',
    'production issue you have faced': 'Encountered an API gateway connection pool exhaustion under sudden traffic surge. Diagnosed thread contention, optimized database keep-alive settings, adjusted socket timeouts, and scaled container pods dynamically.',
    'collaborated with external team members': 'Coordinated directly with cloud vendor enterprise support and third-party API providers to diagnose an intermittent TLS handshake latency spike caused by routing anomalies across regional transit gateways.',
    'why do you want to join mactores': 'Excited by Mactores deep cloud consulting and DevOps automation pedigree, where I can leverage my 4.0 years of AWS EKS, Terraform, and CI/CD expertise to deliver scalable infrastructure solutions.'
}

async def fill_page(page):
    title = await page.title()
    print(f"\n==========================================")
    print(f"Filling full form for: {title}")

    # 1. Textareas (Questions)
    textareas = await page.query_selector_all('textarea')
    for ta in textareas:
        lbl = await ta.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""')
        val = await ta.input_value()
        if not val:
            for k, ans in ANSWERS.items():
                if k in lbl:
                    await ta.fill(ans)
                    print(f"  Filled textarea: '{k}'")
                    break

    # 2. Text Inputs
    inputs = await page.query_selector_all('input[type="text"], input:not([type])')
    for inp in inputs:
        lbl = await inp.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""')
        val = await inp.input_value()
        name = await inp.get_attribute('name') or ''
        
        if 'location' in lbl and not val:
            await inp.fill('Delhi NCR, India')
            print("  Filled Location: Delhi NCR, India")
        elif 'notice' in lbl and not val:
            await inp.fill('30 Days (Serving notice)')
            print("  Filled Notice: 30 Days")
        elif ('experience' in lbl or 'years' in lbl) and not val:
            await inp.fill('4.0 Years')
            print("  Filled Experience: 4.0 Years")
        elif ('ctc' in lbl or 'salary' in lbl or 'compensation' in lbl) and not val:
            if 'offered' in lbl:
                await inp.fill('None')
                print("  Filled Offered CTC: None")
            else:
                await inp.fill('Open / Not Disclosed')
                print("  Filled CTC: Open / Not Disclosed")

    # 3. Radio Buttons
    radios = await page.query_selector_all('input[type="radio"]')
    for r in radios:
        val = (await r.get_attribute('value') or '').lower()
        lbl = (await r.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
        r_label = (await r.evaluate('e => e.closest("label") ? e.closest("label").innerText.toLowerCase() : ""') or '')
        
        # Computer science background -> yes
        if 'computer science' in lbl or 'bachelor' in lbl or 'graduated' in lbl or 'authorized' in lbl or 'aptitude' in lbl or 'serving notice' in lbl:
            if val in ['yes', '1'] or 'yes' in r_label:
                await r.click()
                print(f"  Checked Yes for: {lbl[:40]}...")
        elif 'sponsorship' in lbl or 'sponsor' in lbl:
            if val in ['no', '0'] or 'no' in r_label:
                await r.click()
                print(f"  Checked No for sponsorship: {lbl[:40]}...")

    # 4. Dropdowns (Select elements)
    selects = await page.query_selector_all('select')
    for s in selects:
        lbl = (await s.evaluate('e => e.closest(".application-question") ? e.closest(".application-question").innerText.toLowerCase() : ""') or '')
        opts = await s.query_selector_all('option')
        opt_texts = [(await o.text_content() or '').strip() for o in opts]
        
        if 'united states or india' in lbl or 'authorized' in lbl:
            for opt_t in opt_texts:
                if 'yes' in opt_t.lower():
                    await s.select_option(label=opt_t)
                    print(f"  Selected '{opt_t}' for: {lbl[:40]}")
                    break
        elif 'sponsorship' in lbl:
            for opt_t in opt_texts:
                if 'no' in opt_t.lower():
                    await s.select_option(label=opt_t)
                    print(f"  Selected '{opt_t}' for: {lbl[:40]}")
                    break
        elif 'gender' in lbl:
            for opt_t in opt_texts:
                if 'male' in opt_t.lower() and 'female' not in opt_t.lower():
                    await s.select_option(label=opt_t)
                    print("  Selected Male for Gender")
                    break

    await asyncio.sleep(1)
    print(f"Done filling {title}!")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for page in context.pages:
            if 'lever.co' in page.url:
                await fill_page(page)

asyncio.run(main())
