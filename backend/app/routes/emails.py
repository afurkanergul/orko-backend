# ==============================================================
# 📧 EMAILS ROUTER — Unified Email Fetcher + Gmail Ingestion Bridge
# ==============================================================
from fastapi import APIRouter, Query
from backend.app.integrations.email.email_connector import fetch_user_emails
from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.integrations.email.outlook_client import fetch_outlook_emails
from backend.app.core.vault_manager import load_token
from backend.app.routes.ingest import save_message_to_db
import datetime
import asyncio

# ==============================================================
# 🔗 ROUTER SETUP
# ==============================================================
router = APIRouter(prefix="/emails", tags=["Email Fetcher"])

# --------------------------------------------------------------
# 📬 1️⃣ Fetch Gmail emails directly
# --------------------------------------------------------------
@router.get("/gmail", summary="Get Gmail Emails")
def get_gmail_emails(limit: int = 10):
    """
    Fetch emails directly from Gmail (read-only).
    """
    return fetch_gmail_emails(limit)

# --------------------------------------------------------------
# 📬 2️⃣ Fetch Outlook emails directly
# --------------------------------------------------------------
@router.get("/outlook", summary="Get Outlook Emails")
def get_outlook_emails(limit: int = 10):
    """
    Fetch emails directly from Outlook (read-only).
    """
    return fetch_outlook_emails(limit)

# --------------------------------------------------------------
# 📬 3️⃣ Unified fetch from all sources
# --------------------------------------------------------------
@router.get("/fetch", summary="Fetch Emails")
def fetch_emails(source: str = Query("all", enum=["gmail", "outlook", "all"]), limit: int = 10):
    """
    Fetch emails from the given source (Gmail / Outlook / All)
    """
    emails = fetch_user_emails(source=source, limit=limit)
    return {"count": len(emails), "emails": emails}

# --------------------------------------------------------------
# 📊 4️⃣ Check connection status for Gmail and Outlook
# --------------------------------------------------------------
@router.get("/status", summary="Email Connection Status (Detailed)")
def email_status():
    """
    Returns the authorization status for Gmail and Outlook accounts,
    including when the token was last saved in Vault.
    """
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

# ==============================================================
# 🧩 5️⃣ Gmail Ingestion Bridge — for background automation
# ==============================================================
async def fetch_and_ingest_gmail(limit: int = 10):
    """
    Pull unread Gmail emails using the existing Gmail client
    and push them into ORKO's ingestion pipeline.
    This is used by the background scheduler (Task Scheduler).
    """
    # Run blocking Gmail client in executor so FastAPI isn't blocked
    loop = asyncio.get_running_loop()
    emails = await loop.run_in_executor(None, fetch_gmail_emails, limit)

    print(f"📬 Ingesting {len(emails)} Gmail messages into DB...")

    for e in emails:
        payload = {
            "source": "gmail",
            "sender": e.get("from"),
            "text": f"{e.get('subject', '')}\n\n{e.get('snippet', '')}",
            "timestamp": e.get("date") or datetime.datetime.utcnow().isoformat(),
        }
        try:
            await save_message_to_db(payload)
        except Exception as ex:
            print(f"❌ Failed to ingest email from {e.get('from')}: {ex}")

    print("✅ Gmail ingestion complete.")
