import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

template_url = "https://www.canva.com/templates/EAHDPUZ3X6Q-white-and-blue-minimalist-professional-corporate-ats-resume/"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    # Pick the template page
    page = None
    for pg in context.pages:
        if 'canva.com' in pg.url and 'allcargo' not in pg.url and 'invoices' not in pg.url:
            page = pg
            break
            
    if not page:
        page = context.new_page()
        
    print(f"Navigating to ATS Resume template: {template_url}")
    page.goto(template_url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    
    # Click "Customize this template" button
    cust_btn = page.locator("button:has-text('Customize this template'), a:has-text('Customize this template')")
    if cust_btn.count() > 0:
        print("Found 'Customize this template' button. Clicking...")
        cust_btn.first.click()
        page.wait_for_timeout(5000)
        print("Current Page URL after click:", page.url)
        print("Page Title:", page.title())
    else:
        print("Could not find 'Customize this template' button.")
        for b in page.locator('button, a[role="button"]').all():
            t = b.inner_text().strip()
            if t: print("  - Button:", t)

