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

print("--- Searching Drive for documents with '171' or 'Pipeline' ---")
res = service.files().list(
    q="trashed = false and (name contains 'Pipeline' or name contains 'Tracker' or name contains 'Report' or name contains 'Overview' or name contains 'Career')",
    fields="files(id, name, mimeType, modifiedTime)"
).execute()

for f in res.get('files', []):
    print(f"- {f['name']} | ID: {f['id']} | Mime: {f['mimeType']} | Modified: {f['modifiedTime']}")

