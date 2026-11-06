import json
import sys
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('drive', 'v3', credentials=creds)

print("--- 1. Files inside 'Job Search Pipeline' folder (1hYV0cFZU3gdCNxDWGqyfge_eXc3K43up) ---")
res = service.files().list(
    q="'1hYV0cFZU3gdCNxDWGqyfge_eXc3K43up' in parents and trashed = false",
    fields="files(id, name, mimeType, modifiedTime, size)"
).execute()
for f in res.get('files', []):
    print(f"  - {f['name']} ({f.get('mimeType')}, {f.get('size')} bytes, id: {f['id']})")

print("\n--- 2. Files inside local extracted zip 'scanned_docs/extracted_pipeline' ---")
extracted_dir = r'C:\Users\rah_66160\iTopaz-agents\job\scanned_docs\extracted_pipeline'
if os.path.exists(extracted_dir):
    for root, dirs, files in os.walk(extracted_dir):
        rel = os.path.relpath(root, extracted_dir)
        py_files = [f for f in files if f.endswith(('.py', '.sh', '.json', '.yaml', '.yml', '.md', '.txt'))]
        if py_files:
            print(f"Directory: {rel}")
            for pf in py_files:
                p = os.path.join(root, pf)
                print(f"  - {pf} ({os.path.getsize(p)} bytes)")

