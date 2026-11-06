import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    # NatWest Workday
    print("\n--- NatWest Workday ---")
    workday_url = "https://rbs.wd3.myworkdayjobs.com/RBS/job/Bengaluru/Software-Engineer_R-00285308/apply?source="
    page.goto(workday_url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(3000)
    print("Title:", page.title())
    print("URL:", page.url)
    btns = page.locator("button, a[role='button']").all()
    print("Workday Buttons:")
    for b in btns[:10]:
        t = b.inner_text().strip()
        if t: print("  -", t)

    # AMEX Oracle Cloud
    print("\n--- AMEX Oracle Cloud ---")
    amex_url = "https://careers.americanexpress.com/en/sites/CX_1/job/26015724/"
    page.goto(amex_url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(3000)
    print("Title:", page.title())
    print("URL:", page.url)
    amex_btns = page.locator("button, a[role='button'], a.btn").all()
    print("AMEX Buttons:")
    for b in amex_btns[:10]:
        t = b.inner_text().strip()
        if t: print("  -", t)

    page.close()

