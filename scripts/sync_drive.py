import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'job/gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
drive_service = build('drive', 'v3', credentials=creds)

parent_folder_id = '19CtPRyBF4PqB8h15Hgio1O0YpEMFoktW'

q = f"'{parent_folder_id}' in parents and trashed=false"
results = drive_service.files().list(q=q, fields='files(id, name, mimeType)').execute()
files = results.get('files', [])
print(f'Files in Drive folder ({len(files)}):')
tracker_csv_id = None
for f in files:
    print(f" - {f['name']} ({f['id']}) [{f['mimeType']}]")
    if f['name'] == 'Job_Application_Tracker_Master_2026.csv' or f['name'] == 'tracker.csv':
        tracker_csv_id = f['id']

csv_path = r'job/applications/tracker.csv'
media = MediaFileUpload(csv_path, mimetype='text/csv', resumable=False)

if tracker_csv_id:
    print(f'Updating existing file {tracker_csv_id}...')
    updated = drive_service.files().update(fileId=tracker_csv_id, media_body=media).execute()
    print('Updated successfully:', updated.get('id'))
else:
    print('Creating new tracker file in folder...')
    file_metadata = {
        'name': 'Job_Application_Tracker_Master_2026.csv',
        'parents': [parent_folder_id]
    }
    created = drive_service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
    print('Created successfully:', created)

