import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
drive_service = build('drive', 'v3', credentials=creds)

file_id = '17p_0_0e3NYw685Wnbo5GSiW-UUMbdEzKsTMrGx48lgs'
csv_path = r'C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv'

media = MediaFileUpload(csv_path, mimetype='text/csv', resumable=True)

print('Updating Google Drive spreadsheet with current tracker.csv...')
try:
    updated_file = drive_service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()
    print('Drive spreadsheet successfully updated!', updated_file)
except Exception as e:
    print('Update error:', e)

