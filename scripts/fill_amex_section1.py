import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RESUME_PATH = r"C:\Users\rah_66160\iTopaz-agents\job\resumes\Rahul_Kumar_DevOps_AWS_2026.pdf"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'americanexpress' in pg.url and 'section/1' in pg.url:
            page = pg
            break
            
    if page:
        print("Connected to AMEX Section 1...")
        
        # 1. Upload Resume
        file_input = page.locator("input[type='file']")
        if file_input.count() > 0:
            print("Uploading resume to AMEX...")
            file_input.first.set_input_files(RESUME_PATH)
            page.wait_for_timeout(3000)
            print("Resume uploaded successfully!")
            
        # 2. Fill Name & Contact Details
        def fill_field(sel, val):
            el = page.locator(sel)
            if el.count() > 0 and el.first.is_visible():
                if not el.first.input_value():
                    el.first.fill(val)
                    print(f"Filled {sel} with '{val}'")
                    
        fill_field("input[name='firstName']", "Rahul")
        fill_field("input[name='lastName']", "Kumar")
        fill_field("input[type='tel']", "7210476048")
        fill_field("input[name='addressLine1']", "Delhi, NCR")
        fill_field("input[name='city']", "Delhi")
        fill_field("input[name='postalCode']", "110001")
        fill_field("input[name='region2']", "Delhi")
        
        page.wait_for_timeout(1500)
        
        # 3. Look for Next / Save and Continue button
        next_btn = page.locator("button:has-text('Save and Continue'), button:has-text('Next'), button:has-text('Continue')")
        print(f"Next buttons found: {next_btn.count()}")
        for i in range(next_btn.count()):
            t = next_btn.nth(i).inner_text().strip()
            print(f"  [{i}] '{t}' (Visible: {next_btn.nth(i).is_visible()})")
            
        # Click Next if visible
        for i in range(next_btn.count()):
            btn = next_btn.nth(i)
            if btn.is_visible() and any(w in btn.inner_text().lower() for w in ['next', 'save and continue', 'continue']):
                print(f"Clicking AMEX button: '{btn.inner_text().strip()}'...")
                btn.click()
                page.wait_for_timeout(4000)
                print("AMEX Current URL after submit:", page.url)
                break
    else:
        print("AMEX page not found.")

