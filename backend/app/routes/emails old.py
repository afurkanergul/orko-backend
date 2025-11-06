from fastapi import APIRouter, Query
from backend.app.integrations.email.email_connector import fetch_user_emails

router = APIRouter(prefix="/emails", tags=["Email Fetcher"])

@router.get("/fetch")
def fetch_emails(source: str = Query("all", enum=["gmail", "outlook", "all"]), limit: int = 10):
    """
    Fetch emails from the given source (Gmail / Outlook / All)
    """
    emails = fetch_user_emails(source=source, limit=limit)
    return {"count": len(emails), "emails": emails}

from fastapi import APIRouter
from backend.app.integrations.email.email_connector import fetch_user_emails
from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.integrations.email.outlook_client import fetch_outlook_emails
from backend.app.core.vault_manager import load_token  # 👈 add this import

router = APIRouter(prefix="/emails", tags=["Email Fetcher"])

@router.get("/gmail", summary="Get Gmail Emails")
def get_gmail_emails(limit: int = 10):
    return fetch_gmail_emails(limit)

@router.get("/outlook", summary="Get Outlook Emails")
def get_outlook_emails(limit: int = 10):
    return fetch_outlook_emails(limit)

@router.get("/fetch", summary="Fetch Emails")
def fetch_emails(source: str = "all", limit: int = 10):
    emails = fetch_user_emails(source=source, limit=limit)
    return {"count": len(emails), "emails": emails}

# ✅ NEW: quick connection status
@router.get("/status", summary="Email Connection Status (Detailed)")
def email_status():
    """
    Returns the authorization status for Gmail and Outlook accounts,
    including when the token was last saved.
    """
    from backend.app.core.vault_manager import load_token

    gmail = load_token("gmail")
    outlook = load_token("outlook")

    def summarize(token):
        if not token:
            return {"authorized": False}
        return {
            "authorized": True,
            "saved_at": token.get("saved_at"),
            "email_hint": token.get("client_email") or token.get("username"),
        }

    return {
        "gmail": summarize(gmail),
        "outlook": summarize(outlook)
    }
# 🧩  Gmail ingestion bridge
from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.routes.ingest import save_message_to_db
import datetime

async def fetch_and_ingest_gmail(limit=10):
    emails = fetch_gmail_emails(limit)
    for e in emails:
        payload = {
            "source": "gmail",
            "sender": e.get("from"),
            "text": f"{e.get('subject','')}\n\n{e.get('snippet','')}",
            "timestamp": e.get("date") or datetime.datetime.utcnow().isoformat(),
        }
        await save_message_to_db(payload)
