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

print("--- Querying Google Drive for all folders and files ---")
query = "trashed = false"
page_token = None
all_files = []

while True:
    res = service.files().list(
        q=query,
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, parents)",
        pageToken=page_token
    ).execute()
    all_files.extend(res.get('files', []))
    page_token = res.get('nextPageToken')
    if not page_token or len(all_files) >= 500:
        break

print(f"Total files found in Google Drive: {len(all_files)}")
print("\nFiles/Folders with code, script, zip, or technical keywords:")
code_exts = ('.py', '.sh', '.js', '.ts', '.yaml', '.yml', '.json', '.zip', '.tar', '.gz', '.sql', '.tf', '.cpp', '.java', '.go')
for f in all_files:
    name = f['name']
    mime = f.get('mimeType', '')
    size = f.get('size', 'N/A')
    if any(name.lower().endswith(ext) for ext in code_exts) or any(k in name.lower() for k in ['code', 'pipeline', 'script', 'project', 'repo', 'devops', 'automation']):
        print(f"- {name} | {mime} | Size: {size} bytes | ID: {f['id']}")

