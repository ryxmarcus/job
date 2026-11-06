import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
drive_service = build('drive', 'v3', credentials=creds)

folder_id = '1hYV0cFZU3gdCNxDWGqyfge_eXc3K43up'
res = drive_service.files().list(
    q=f"'{folder_id}' in parents and trashed = false",
    fields='files(id, name, mimeType)'
).execute()

print(f"Items in Job Search Pipeline ({folder_id}):")
for f in res.get('files', []):
    print(f"- {f['name']} | ID: {f['id']} | Mime: {f['mimeType']}")
    if f['mimeType'] == 'application/vnd.google-apps.folder':
        # Subfiles
        sub = drive_service.files().list(
            q=f"'{f['id']}' in parents and trashed = false",
            fields='files(id, name, mimeType)'
        ).execute()
        for sf in sub.get('files', [])[:10]:
            print(f"    * {sf['name']} | ID: {sf['id']}")

