import sys
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    # 1. Syfe on Instahyre
    print("\n--- 1. Testing Syfe on Instahyre ---")
    page.goto("https://www.instahyre.com/job-444216-senior-site-reliability-engineer-at-syfe-gurgaon/", wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(2500)
    apply_btn = page.locator("button:has-text('Apply now'), a:has-text('Apply now')")
    if apply_btn.count() > 0:
        print("Clicking 'Apply now' on Instahyre...")
        apply_btn.first.click()
        page.wait_for_timeout(2500)
        print("Page URL after click:", page.url)
        modals = page.locator(".modal, [role='dialog'], form")
        print("Modal / Form visible:", modals.count())
        if modals.count() > 0:
            print("Modal Text:", modals.first.inner_text()[:200])

    # 2. NatWest Workday
    print("\n--- 2. Testing NatWest Workday Link ---")
    workday_url = "https://rbs.wd3.myworkdayjobs.com/RBS/job/Bengaluru/Software-Engineer_R-00285308/apply?source="
    page.goto(workday_url, wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(3000)
    print("Workday Page Title:", page.title())
    print("Workday URL:", page.url)
    workday_ctas = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a, button')).map(el => el.innerText.trim()).filter(t => t.toLowerCase().includes('autofill') || t.toLowerCase().includes('apply') || t.toLowerCase().includes('sign in'));
    }""")
    print("Workday CTAs:", workday_ctas)

    # 3. American Express
    print("\n--- 3. Testing American Express Oracle Cloud ---")
    page.goto("https://careers.americanexpress.com/en/sites/CX_1/job/26015724/", wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(4000)
    amex_buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button, a')).map(el => ({ text: el.innerText.trim(), id: el.id, cls: el.className })).filter(x => x.text.toLowerCase().includes('apply'));
    }""")
    print("AMEX Apply Buttons:", amex_buttons)

    # 4. Postman & Hasura direct links from myinternships.in
    print("\n--- 4. Extracting direct links for Postman & Hasura ---")
    for comp, u in [("Postman", "https://myinternships.in/jobs/postman-devops-engineer-gurugram-1683be"),
                    ("Hasura", "https://myinternships.in/jobs/hasura-devops-engineer-gurugram-6131af")]:
        page.goto(u, wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(2000)
        ext_links = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => !h.includes('myinternships.in') && h.startsWith('http'));
        }""")
        print(f"{comp} external links found: {ext_links}")

    page.close()

