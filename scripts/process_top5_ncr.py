import sys
import os
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TARGET_JOBS = [
    {
        "id": "J154",
        "company": "Postman",
        "title": "DevOps Engineer",
        "url": "https://myinternships.in/jobs/postman-devops-engineer-gurugram-1683be",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf"
    },
    {
        "id": "J174",
        "company": "American Express",
        "title": "Data & Cloud Infrastructure Engineer II",
        "url": "https://careers.americanexpress.com/en/sites/CX_1/job/26015724/",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf"
    },
    {
        "id": "J175",
        "company": "Syfe",
        "title": "Senior Site Reliability Engineer",
        "url": "https://www.instahyre.com/job-444216-senior-site-reliability-engineer-at-syfe-gurgaon/",
        "resume": "Site_Reliability_Engineer_Rahul_Kumar.pdf"
    },
    {
        "id": "J152",
        "company": "NatWest Group",
        "title": "Platform & Software Engineer",
        "url": "https://jobs.natwestgroup.com/jobs/18256840-software-engineer",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf"
    },
    {
        "id": "J153",
        "company": "Hasura",
        "title": "DevOps Engineer",
        "url": "https://myinternships.in/jobs/hasura-devops-engineer-gurugram-6131af",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf"
    }
]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    for job in TARGET_JOBS:
        print(f"\n==========================================")
        print(f"[{job['id']}] {job['company']} - {job['title']}")
        print(f"URL: {job['url']}")
        try:
            resp = page.goto(job['url'], wait_until='domcontentloaded', timeout=25000)
            page.wait_for_timeout(2500)
            print(f"HTTP Status: {resp.status if resp else 'N/A'}")
            print(f"Title: {page.title()}")
            print(f"Final URL: {page.url}")
            
            # Inspect apply buttons or forms
            buttons = page.evaluate("""() => {
                const list = [];
                document.querySelectorAll('button, a[role="button"], a.btn, a[class*="apply" i], button[class*="apply" i]').forEach(el => {
                    const txt = el.innerText?.trim() || '';
                    if (txt && (txt.toLowerCase().includes('apply') || txt.toLowerCase().includes('submit') || txt.toLowerCase().includes('register'))) {
                        list.push({ text: txt.slice(0, 40), href: el.getAttribute('href') || '' });
                    }
                });
                return list;
            }""")
            print(f"Apply Buttons / CTAs found: {buttons}")
        except Exception as e:
            print(f"Error accessing {job['company']}: {e}")

    page.close()

