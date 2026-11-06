import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'americanexpress' in pg.url and 'section/3' in pg.url:
            page = pg
            break
            
    if page:
        print("Connected to AMEX Section 3:", page.url)
        print("Text Preview:\n", page.inner_text('body'))

