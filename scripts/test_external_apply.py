import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

test_url = "https://www.naukri.com/job-listings-site-reliability-engineer-ii-akamai-technologies-bengaluru-3-to-7-years-021126500484"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = context.new_page()
    print("Navigating to Akamai job on Naukri...")
    page.goto(test_url, wait_until='domcontentloaded', timeout=25000)
    page.wait_for_timeout(2500)
    
    btn = page.locator("button:has-text('Apply on company site'), a:has-text('Apply on company site'), [class*='apply-button']")
    print("Buttons found:", btn.count())
    for i in range(btn.count()):
        print(f"  [{i}] '{btn.nth(i).inner_text().strip()}'")
        
    if btn.count() > 0:
        with context.expect_page(timeout=10000) as new_page_info:
            print("Clicking 'Apply on company site'...")
            btn.first.click()
            
        dest_page = new_page_info.value
        dest_page.wait_for_load_state('domcontentloaded', timeout=15000)
        print("Redirected to external page!")
        print("Dest URL:", dest_page.url)
        print("Dest Title:", dest_page.title())
        dest_page.close()
        
    page.close()

