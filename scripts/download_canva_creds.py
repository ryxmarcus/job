import json
import sys
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

token_path = r'C:\Users\rah_66160\iTopaz-agents\job\gdrive_token.json'
with open(token_path, 'r') as f:
    token_data = json.load(f)

creds = Credentials.from_authorized_user_info(token_data)
service = build('drive', 'v3', credentials=creds)

file_id = '114z7ZcVftPcc9-MHqpecNREBz5gMu0UTyPjrEj2rUJg'
request = service.files().export_media(fileId=file_id, mimeType='text/plain')
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while not done:
    status, done = downloader.next_chunk()

content = fh.getvalue().decode('utf-8')
print("=== Content of Canva API Credentials - Rahul Kumar ===")
print(content)

with open(r'C:\Users\rah_66160\iTopaz-agents\job\canva_credentials.txt', 'w', encoding='utf-8') as out:
    out.write(content)
print("\nSaved to C:\\Users\\rah_66160\\iTopaz-agents\\job\\canva_credentials.txt")

