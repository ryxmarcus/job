import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'DAHZxncrm0w' in pg.url:
            page = pg
            break
            
    if page:
        print("Connected to Canva editor:", page.url)
        print("Title:", page.title())
        
        # Check title input or rename design
        title_el = page.locator("input[aria-label*='title' i], [data-testid='design-title'] input, [class*='titleInput']")
        if title_el.count() > 0:
            print("Current title field value:", title_el.first.input_value())
            title_el.first.fill("Rahul Kumar - DevOps SRE ATS Resume (2026)")
            title_el.first.press("Enter")
            print("Renamed design to: Rahul Kumar - DevOps SRE ATS Resume (2026)")
        else:
            print("Title input selector not matched directly.")
    else:
        print("Design page not found in context.")

