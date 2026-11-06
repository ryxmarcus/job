import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
sheets_service = build('sheets', 'v4', credentials=creds)

sheet_id = '17p_0_0e3NYw685Wnbo5GSiW-UUMbdEzKsTMrGx48lgs'
sheet_meta = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()

print('Title:', sheet_meta.get('properties', {}).get('title'))
for s in sheet_meta.get('sheets', []):
    props = s.get('properties', {})
    print(f"Sheet Name: '{props.get('title')}' | Grid: {props.get('gridProperties')}")

