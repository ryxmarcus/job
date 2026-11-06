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

sheet_id = '17p_0_0e3NYw685Wnbo5GSiW-UUMbdEzKsTMrGx48lgs'
print('Exporting Google Sheet via Drive API as CSV...')
content = drive_service.files().export(fileId=sheet_id, mimeType='text/csv').execute()

out_path = r'C:\Users\rah_66160\iTopaz-agents\job\drive_job_tracker.csv'
with open(out_path, 'wb') as f:
    f.write(content)

print(f'Saved to {out_path} ({len(content)} bytes)')

# Read first few lines
with open(out_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = [f.readline() for _ in range(15)]
    print('Header & First rows:')
    for l in lines:
        print(' ', l.strip()[:150])

