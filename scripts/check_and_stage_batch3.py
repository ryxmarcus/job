import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TEST_JOBS = [
    {'id': 'J029', 'company': 'Zimperium', 'role': 'Site Reliability Engineer - India', 'url': 'https://jobs.lever.co/zimperium/29aff3bb-b00f-457c-9ebb-70f3804c3fa6'},
    {'id': 'J031', 'company': 'Drivetrain', 'role': 'Site Reliability Engineer - SRE', 'url': 'https://jobs.lever.co/drivetrain/d1bc29ad-d0aa-47c8-8785-1094f279ccff'},
    {'id': 'J002', 'company': 'AHEAD', 'role': 'AI Platform Engineer', 'url': 'https://jobs.lever.co/thinkahead/9bb45260-8225-4175-972e-a15c3213bf30'},
    {'id': 'J024', 'company': 'Particle41', 'role': 'DevOps Engineer', 'url': 'https://job-boards.greenhouse.io/particle41llc/jobs/5018960008'},
    {'id': 'J028', 'company': 'Cohere Health', 'role': 'DevOps Engineer', 'url': 'https://job-boards.greenhouse.io/coherehealth/jobs/8037633003'},
    {'id': 'J091', 'company': 'GitLab', 'role': 'Staff SRE Environment Automation', 'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8800489002'},
    {'id': 'J092', 'company': 'GitLab', 'role': 'Staff SRE Monitoring', 'url': 'https://job-boards.greenhouse.io/gitlab/jobs/8615268002'},
    {'id': 'J001', 'company': 'Teikametrics', 'role': 'Senior SRE', 'url': 'https://job-boards.greenhouse.io/teikametrics/jobs/4361177009'},
    {'id': 'J025', 'company': 'Bosch', 'role': 'DevOps Engineer K8s', 'url': 'https://jobs.smartrecruiters.com/BoschGroup/744000155720139-devops-engineer-application-deployment-configuration-k8s-'}
]

async def check_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        
        for job in TEST_JOBS:
            page = await context.new_page()
            try:
                print(f"Checking [{job['id']}] {job['company']} - {job['role']}...")
                resp = await page.goto(job['url'], wait_until='domcontentloaded', timeout=20000)
                status = resp.status if resp else 'No resp'
                body = await page.inner_text('body')
                title = await page.title()
                
                is_closed = False
                for term in ['position has been closed', 'job no longer available', 'page not found', '404', 'no longer accepting']:
                    if term in body.lower():
                        is_closed = True
                        break
                
                print(f" -> Status: {status} | Title: {title} | Closed: {is_closed}")
            except Exception as e:
                print(f" -> Error: {e}")
            finally:
                await page.close()

if __name__ == '__main__':
    asyncio.run(check_jobs())

