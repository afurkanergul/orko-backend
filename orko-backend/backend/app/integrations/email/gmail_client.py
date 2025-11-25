from __future__ import print_function
import sys, pathlib, os, json
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from backend.app.core.vault_manager import save_token, load_token
from google.auth.transport.requests import Request


def ensure_valid_creds(creds, service_name: str):
    """Auto-refresh credentials if expired, then save back to vault."""
    if creds and creds.expired and creds.refresh_token:
        print(f"♻️ Refreshing {service_name} token...")
        creds.refresh(Request())
        save_token(service_name, json.loads(creds.to_json()))
    return creds


# Gmail read-only permission
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Use absolute paths to avoid confusion
ROOT = pathlib.Path(__file__).resolve().parents[4]
CREDS = ROOT / "backend/app/integrations/email/credentials_gmail.json"
TOKEN_FILE = ROOT / "backend/app/integrations/email/token_gmail.json"


def fetch_gmail_emails(limit=10):
    """Connect to Gmail and return email metadata using Vault-stored or local token."""
    creds = None

    # 🧠 1️⃣ Try loading from vault first
    token_data = load_token("gmail")

    if token_data:
        # Inject missing client_id/client_secret if needed
        if "client_id" not in token_data or "client_secret" not in token_data:
            with open(CREDS, "r", encoding="utf-8") as f:
                creds_info = json.load(f).get("installed", {})
                token_data["client_id"] = creds_info.get("client_id")
                token_data["client_secret"] = creds_info.get("client_secret")

        creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    # 🧩 2️⃣ If vault empty or token invalid → trigger OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            save_token("gmail", json.loads(creds.to_json()))
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS), SCOPES)
            creds = flow.run_local_server(port=0)

            # Save both locally and in vault
            token_json = json.loads(creds.to_json())
            save_token("gmail", token_json)
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(token_json, f, indent=2)

    # ♻️ Ensure token is valid or refreshed before building the service
    creds = ensure_valid_creds(creds, "gmail")

    # 📬 3️⃣ Fetch richer email metadata
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(
        userId="me",
        maxResults=limit,
        labelIds=["INBOX"]
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()

        headers = {h["name"].lower(): h["value"] for h in detail.get("payload", {}).get("headers", [])}
        snippet = detail.get("snippet", "")
        labels = detail.get("labelIds", [])

        emails.append({
            "source": "gmail",
            "from": headers.get("from"),
            "to": headers.get("to"),
            "subject": headers.get("subject"),
            "date": headers.get("date"),
            "snippet": snippet,
            "unread": "UNREAD" in labels
        })

    return emails  # ✅ correctly indented inside the function


if __name__ == "__main__":
    print("Connecting to Gmail...\n")
    try:
        emails = fetch_gmail_emails(10)
        print("✅ Gmail connected! Here are your latest subjects:\n")
        for i, e in enumerate(emails, start=1):
            print(f"{i:02d}. {e['subject']}")
    except Exception as e:
        print("❌ Error:", e)
