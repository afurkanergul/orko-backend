# app/integrations/drive_integration.py
import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

GOOGLE_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
CREDENTIALS_PATH = Path("app/integrations/google/credentials.json")


def list_drive_files():
    """
    Opens a browser once (first run), asks your permission,
    and prints your recent Google Drive files (name + id).
    """
    if not CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"❌ Google credentials.json not found at {CREDENTIALS_PATH}."
        )

    # OAuth login flow
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GOOGLE_SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)

    # List first 10 files
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])
    for f in files:
        print(f"{f['name']} — {f['id']}")
    return files
