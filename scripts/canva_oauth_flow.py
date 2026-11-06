import http.server
import socketserver
import urllib.parse
import urllib.request
import base64
import hashlib
import os
import json
import secrets
import sys
import threading
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CLIENT_ID = os.getenv("CANVA_CLIENT_ID", "YOUR_CANVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("CANVA_CLIENT_SECRET", "YOUR_CANVA_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:3000/oauth/callback"
TOKEN_PATH = r"C:\Users\rah_66160\iTopaz-agents\job\canva_token.json"

# PKCE generation
def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)
state = secrets.token_urlsafe(16)

# Standard Canva Connect scopes
SCOPES = "design:content:read design:content:write design:meta:read folder:read folder:write asset:read asset:write profile:read"

auth_params = {
    "code_challenge": code_challenge,
    "code_challenge_method": "S256",
    "scope": SCOPES,
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "state": state
}
auth_url = f"https://www.canva.com/api/oauth/authorize?{urllib.parse.urlencode(auth_params)}"

received_code = None

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global received_code
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/oauth/callback":
            params = urllib.parse.parse_qs(parsed.query)
            if "code" in params:
                received_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Canva Authentication Successful!</h1><p>You can close this tab now.</p></body></html>")
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                err = params.get("error_description", ["Unknown error"])[0]
                self.wfile.write(f"<html><body><h1>Authentication Failed</h1><p>{err}</p></body></html>".encode())
    def log_message(self, format, *args):
        pass

def start_server():
    with socketserver.TCPServer(("127.0.0.1", 3000), OAuthHandler) as httpd:
        httpd.timeout = 120
        while not received_code:
            httpd.handle_request()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

print("Local OAuth listener listening on http://127.0.0.1:3000/oauth/callback")
print(f"Opening Canva Authorization URL:\n{auth_url}\n")

# Navigate the Edge browser to the authorization URL
try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        # Open a new tab for authorization
        auth_page = context.new_page()
        auth_page.goto(auth_url, wait_until='domcontentloaded', timeout=30000)
        print("Navigated browser to Canva Authorization page.")
        
        # Look for Authorize/Allow button and auto-click if presented
        auth_page.wait_for_timeout(3000)
        allow_btn = auth_page.locator("button:has-text('Allow'), button:has-text('Authorize'), button:has-text('Connect')")
        if allow_btn.count() > 0 and allow_btn.first.is_visible():
            print("Auto-clicking Canva 'Allow' button...")
            allow_btn.first.click()
except Exception as e:
    print(f"Note on browser navigation: {e}")

# Wait for code
print("Waiting for OAuth callback...")
timeout = 60
start_time = os.times().elapsed
import time
while not received_code and (time.time() - start_time < timeout):
    time.sleep(1)

if not received_code:
    print("Timed out waiting for Canva authorization code.")
    sys.exit(1)

print(f"Received Authorization Code: {received_code[:10]}...")

# Exchange code for access token at https://api.canva.com/rest/v1/oauth/token
token_url = "https://api.canva.com/rest/v1/oauth/token"
token_data = urllib.parse.urlencode({
    "grant_type": "authorization_code",
    "code_verifier": code_verifier,
    "code": received_code,
    "redirect_uri": REDIRECT_URI
}).encode('utf-8')

# Basic Auth header with client_id:client_secret
auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode('utf-8')).decode('utf-8')

token_req = urllib.request.Request(
    token_url,
    data=token_data,
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}",
        "User-Agent": "Antigravity/1.0"
    }
)

try:
    with urllib.request.urlopen(token_req) as resp:
        token_json = json.loads(resp.read().decode('utf-8'))
        with open(TOKEN_PATH, 'w', encoding='utf-8') as f:
            json.dump(token_json, f, indent=2)
        print("Successfully obtained and saved Canva access token to", TOKEN_PATH)
        print("Token scope:", token_json.get("scope"))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    sys.exit(1)
except Exception as e:
    print(f"Error requesting token: {e}")
    sys.exit(1)

