import subprocess
import time
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

edge_cmd = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '--remote-debugging-port=9222',
    r'--user-data-dir=C:\Users\rah_66160\.edge_debug_profile'
]

print("Starting Edge with remote debugging...")
edge_proc = subprocess.Popen(edge_cmd)
time.sleep(2.5)

try:
    with sync_playwright() as p:
        print("Connecting Playwright over CDP to port 9222...")
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        print("Navigating to Naukri...")
        page.goto('https://www.naukri.com/mnjuser/profile', wait_until='domcontentloaded', timeout=20000)
        page.wait_for_timeout(3000)
        
        title = page.title()
        print(f"Page Title: {title}")
        
        # Check user profile name
        user_name_el = page.query_selector('.user-name, [class*="userName"], .name')
        if user_name_el:
            print(f"Logged in user: {user_name_el.inner_text().strip()}")
        else:
            body_txt = page.inner_text('body')
            print("Snippet:", body_txt[:300].replace('\n', ' -- '))
            
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Script finished.")
