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

# Let's inspect the file metadata on Drive
meta = drive_service.files().get(fileId=file_id, fields='id, name, mimeType, parents').execute()
print('Drive File Meta:', meta)

