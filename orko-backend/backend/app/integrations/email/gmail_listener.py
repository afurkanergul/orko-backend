# backend/app/integrations/email/gmail_listener.py
# 🧙‍♂️ ORKO Gmail Listener – auto-fetch unread emails and save to DB

import asyncio
import datetime
from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.routes.ingest import save_message_to_db

async def poll_gmail_and_ingest(limit: int = 10):
    """
    Periodically fetch unread Gmail messages and store them into DB.
    """
    try:
        emails = fetch_gmail_emails(limit=limit)
        for e in emails:
            payload = {
                "source": "gmail",
                "sender": e.get("from"),
                "text": f"{e.get('subject','')}\n\n{e.get('snippet','')}",
                "timestamp": e.get("date") or datetime.datetime.utcnow().isoformat(),
            }
            await save_message_to_db(payload)
        print(f"✅ Gmail Listener saved {len(emails)} emails at {datetime.datetime.utcnow().isoformat()}")
    except Exception as exc:
        print(f"❌ Gmail Listener error: {exc}")

async def start_gmail_listener(interval_minutes: int = 15):
    """
    Runs forever: wakes every <interval_minutes>, pulls new Gmail, saves to DB.
    """
    while True:
        await poll_gmail_and_ingest(limit=10)
        print(f"⏰ Sleeping {interval_minutes} min until next check...")
        await asyncio.sleep(interval_minutes * 60)
