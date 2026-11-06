import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = "https://www.canva.com/design?create&template=EAHDPUZ3X6Q"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'EAHDPUZ3X6Q' in pg.url:
            page = pg
            break
            
    if not page:
        page = context.new_page()
        
    print(f"Navigating to: {url}")
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(6000)
    print("New Page URL:", page.url)
    print("New Page Title:", page.title())

