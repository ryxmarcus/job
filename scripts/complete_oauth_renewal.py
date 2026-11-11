import json
import sys
import time
import threading
import subprocess
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = Path(r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json')

with open(token_path, 'r') as f:
    orig_token = json.load(f)

client_config = {
    'installed': {
        'client_id': orig_token['client_id'],
        'client_secret': orig_token['client_secret'],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': orig_token.get('token_uri', 'https://oauth2.googleapis.com/token'),
        'redirect_uris': ['http://localhost']
    }
}

scopes = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.readonly'
]

flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

# Start Edge with debug profile
edge_cmd = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '--remote-debugging-port=9222',
    r'--user-data-dir=C:\Users\rah_66160\.edge_debug_profile'
]
proc = subprocess.Popen(edge_cmd)
time.sleep(2.5)

creds = None
flow_error = None

def run_server():
    global creds, flow_error
    try:
        print("[Server Thread] Starting local server on port 8088...", flush=True)
        creds = flow.run_local_server(
            host='localhost',
            port=8088,
            authorization_prompt_message='',
            open_browser=False
        )
        print("[Server Thread] Received credentials successfully!", flush=True)
    except Exception as e:
        flow_error = e
        print(f"[Server Thread] Error: {e}", flush=True)

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(1.5)

auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print(f"Generated Auth URL with full Drive scopes. Navigating in Edge...", flush=True)

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.new_page()
        
        page.goto(auth_url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # Step 1: Click account if accountchooser is active
        try:
            acct = page.locator("text='rk58743k@gmail.com'").first
            if acct.is_visible(timeout=3000):
                print("[Action] Found account rk58743k@gmail.com, clicking...", flush=True)
                acct.click()
                time.sleep(4)
        except Exception:
            pass

        # Monitor loop for warning or consent pages
        for loop_idx in range(25):
            if creds is not None:
                print("[Loop] Creds obtained in server thread!", flush=True)
                break
                
            try:
                page.wait_for_load_state('domcontentloaded', timeout=3000)
            except Exception:
                pass
                
            try:
                title = page.title()
                url = page.url
            except Exception:
                time.sleep(1)
                continue

            # Check for redirect complete
            if "localhost:8088" in url or "127.0.0.1:8088" in url:
                print("[Action] Reached localhost:8088 redirect!", flush=True)
                time.sleep(3)
                break

            # Handle Warning Screen ("Google hasn't verified this app")
            if "warning" in url or "verified" in title.lower():
                try:
                    cont = page.locator("button:has-text('Continue'), a:has-text('Continue')").first
                    if cont.is_visible(timeout=2000):
                        print("[Action] Clicking Continue on warning screen...", flush=True)
                        cont.click()
                        time.sleep(4)
                        continue
                except Exception:
                    pass

            # Handle Consent Screen ("Antigravity Drive wants to access...")
            if "consent" in url or "request" in url:
                # Check select all / all checkboxes
                try:
                    cbs = page.query_selector_all("input[type='checkbox']")
                    for cb in cbs:
                        if not cb.is_checked():
                            cb.check()
                            print("  Checked permission checkbox", flush=True)
                except Exception:
                    pass

                # Click Continue / Allow
                try:
                    allow_btn = page.locator("button:has-text('Continue'), button:has-text('Allow'), #submit_approve_access").first
                    if allow_btn.is_visible(timeout=2000):
                        print("[Action] Clicking Continue/Allow button...", flush=True)
                        allow_btn.click()
                        time.sleep(4)
                        continue
                except Exception:
                    pass

            time.sleep(2)

        try:
            page.close()
        except Exception:
            pass
except Exception as e:
    print(f"Browser interaction error: {e}", flush=True)

# Wait for server thread to finish
t.join(timeout=10)

if creds:
    print("\n==========================================", flush=True)
    print("SUCCESS! Full Drive Credentials obtained!", flush=True)
    print("==========================================", flush=True)
    new_token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    with open(token_path, 'w') as f:
        json.dump(new_token_data, f, indent=2)
    print(f"Saved renewed token with scopes {creds.scopes} to: {token_path}", flush=True)
else:
    print("\nCredentials not obtained. Error:", flow_error, flush=True)

proc.terminate()
