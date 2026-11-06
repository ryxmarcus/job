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

folders = [
    ('01 Job Postings', '1zpa620UFUaJUCswub0hrwMxwbwCyqSCU'),
    ('02 Tailored CVs', '1Gl_PbWgAUZXjt3M9diWdeQCr93_QovJo'),
    ('03 Cover Letters', '1ZA6NMuTFF8T47L-ZFqFnGp9RI4U-6yc1'),
    ('04 Interview Prep', '16WhxpApekQJE09otVc5ry-40FTVrOqYf'),
    ('05 Offers & Admin', '1Q0_79ORYpA003Wg4GZC4LwjrbVtN-Ru-')
]

for name, fid in folders:
    res = service.files().list(
        q=f"'{fid}' in parents and trashed = false",
        fields='files(id, name, mimeType, size)'
    ).execute()
    files = res.get('files', [])
    print(f"=== {name} ({len(files)} items) ===")
    for file in files:
        print(f"  - {file['name']} ({file.get('mimeType')})")

