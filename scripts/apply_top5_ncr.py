import sys
import os
import json
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RESUME_PATH = r"C:\Users\rah_66160\iTopaz-agents\job\resumes\Rahul_Kumar_DevOps_AWS_2026.pdf"
SRE_RESUME_PATH = r"C:\Users\rah_66160\iTopaz-agents\job\resumes\Rahul_Kumar_Site_Reliability_Engineer_CV.pdf"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    # ----------------------------------------------------
    # 1. NatWest Group Workday: https://rbs.wd3.myworkdayjobs.com/RBS/job/Bengaluru/Software-Engineer_R-00285308/apply?source=
    # ----------------------------------------------------
    print("\n--- [J152] NatWest Group Workday Execution ---")
    page_natwest = context.new_page()
    try:
        page_natwest.goto("https://rbs.wd3.myworkdayjobs.com/RBS/job/Bengaluru/Software-Engineer_R-00285308/apply?source=", wait_until='domcontentloaded', timeout=30000)
        page_natwest.wait_for_timeout(3500)
        
        # Accept cookies if banner visible
        cookie_btn = page_natwest.locator("button:has-text('Accept Cookies')")
        if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
            cookie_btn.first.click()
            page_natwest.wait_for_timeout(1500)
            
        print("NatWest Workday Loaded. Current URL:", page_natwest.url)
        # Look for "Autofill with Resume" or "Apply Manually"
        autofill_btn = page_natwest.locator("a:has-text('Autofill with Resume'), button:has-text('Autofill with Resume'), a:has-text('Apply Manually'), button:has-text('Apply Manually')")
        print(f"Workday Apply Options: {autofill_btn.count()}")
        for i in range(autofill_btn.count()):
            print(f"  Option {i}: {autofill_btn.nth(i).inner_text().strip()}")
            
        if autofill_btn.count() > 0:
            print("Clicking first apply option on Workday...")
            autofill_btn.first.click()
            page_natwest.wait_for_timeout(3000)
            print("URL after apply option click:", page_natwest.url)
            
            # Check if sign in or registration page appears
            inputs = page_natwest.locator("input:visible")
            print(f"Visible inputs on Workday: {inputs.count()}")
    except Exception as e:
        print(f"NatWest Workday Error: {e}")

    # ----------------------------------------------------
    # 2. Syfe on Instahyre: https://www.instahyre.com/job-444216-senior-site-reliability-engineer-at-syfe-gurgaon/
    # ----------------------------------------------------
    print("\n--- [J175] Syfe Instahyre Execution ---")
    page_syfe = context.new_page()
    try:
        page_syfe.goto("https://www.instahyre.com/job-444216-senior-site-reliability-engineer-at-syfe-gurgaon/", wait_until='domcontentloaded', timeout=25000)
        page_syfe.wait_for_timeout(2500)
        apply_btn = page_syfe.locator("button:has-text('Apply now'), a:has-text('Apply now')")
        if apply_btn.count() > 0 and apply_btn.first.is_visible():
            print("Clicking 'Apply now' on Syfe Instahyre...")
            apply_btn.first.click()
            page_syfe.wait_for_timeout(2500)
            
            # Fill candidate registration / login fields if visible
            name_input = page_syfe.locator("input[name*='name' i], input[placeholder*='name' i]")
            email_input = page_syfe.locator("input[type='email'], input[name*='email' i]")
            
            if name_input.count() > 0 and name_input.first.is_visible() and not name_input.first.input_value():
                print("Filling Name: Rahul Kumar")
                name_input.first.fill("Rahul Kumar")
            if email_input.count() > 0 and email_input.first.is_visible() and not email_input.first.input_value():
                print("Filling Email: rk58743k@gmail.com")
                email_input.first.fill("rk58743k@gmail.com")
                
            print("Syfe Instahyre application flow primed.")
    except Exception as e:
        print(f"Syfe Error: {e}")

    # ----------------------------------------------------
    # 3. American Express: https://careers.americanexpress.com/en/sites/CX_1/job/26015724/
    # ----------------------------------------------------
    print("\n--- [J174] American Express Execution ---")
    page_amex = context.new_page()
    try:
        page_amex.goto("https://careers.americanexpress.com/en/sites/CX_1/job/26015724/", wait_until='domcontentloaded', timeout=25000)
        page_amex.wait_for_timeout(4000)
        
        # In Oracle CX_1, find Apply button
        apply_cta = page_amex.locator("button:has-text('Apply'), a:has-text('Apply'), [data-automation-id*='apply']")
        print(f"AMEX Apply CTAs: {apply_cta.count()}")
        if apply_cta.count() > 0:
            for i in range(apply_cta.count()):
                t = apply_cta.nth(i).inner_text().strip()
                print(f"  CTA {i}: {t}")
            print("Clicking AMEX Apply button...")
            apply_cta.first.click()
            page_amex.wait_for_timeout(4000)
            print("AMEX URL after click:", page_amex.url)
    except Exception as e:
        print(f"AMEX Error: {e}")

    # ----------------------------------------------------
    # 4 & 5. Postman & Hasura on myinternships.in
    # ----------------------------------------------------
    print("\n--- [J154 & J153] Postman & Hasura Execution ---")
    page_mi = context.new_page()
    try:
        page_mi.goto("https://myinternships.in/jobs/postman-devops-engineer-gurugram-1683be", wait_until='domcontentloaded', timeout=25000)
        page_mi.wait_for_timeout(2500)
        login_btn = page_mi.locator("a:has-text('Login to Apply'), button:has-text('Login to Apply')")
        print(f"MyInternships Apply Button: {login_btn.count()}")
        if login_btn.count() > 0:
            print("Login to Apply link URL:", login_btn.first.get_attribute('href'))
    except Exception as e:
        print(f"MyInternships Error: {e}")

    print("\nPriority 1 NCR Automation Steps Initialized.")
