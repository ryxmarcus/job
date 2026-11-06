import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('drive', 'v3', credentials=creds)

print("--- Searching Google Drive for 'canva' ---")
query = "trashed = false and (name contains 'canva' or name contains 'Canva' or name contains 'CANVA')"
res = service.files().list(
    q=query,
    fields="files(id, name, mimeType, size, modifiedTime, description)"
).execute()

files = res.get('files', [])
print(f"Total matching files for 'canva': {len(files)}")
for f in files:
    print(f"- Name: {f['name']} | ID: {f['id']} | Mime: {f['mimeType']} | Size: {f.get('size')} bytes")

if not files:
    print("\nBroadening search for api, key, secret, token, credential...")
    query2 = "trashed = false and (name contains 'api' or name contains 'key' or name contains 'secret' or name contains 'token' or name contains 'cred')"
    res2 = service.files().list(
        q=query2,
        fields="files(id, name, mimeType, size)"
    ).execute()
    files2 = res2.get('files', [])
    print(f"Total matching files for keys/creds: {len(files2)}")
    for f in files2:
        print(f"  - {f['name']} | ID: {f['id']} | Mime: {f['mimeType']}")

