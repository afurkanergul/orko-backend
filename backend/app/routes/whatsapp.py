# backend/app/routes/whatsapp.py

from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from twilio.request_validator import RequestValidator
from twilio.rest import Client
import os, json, asyncio, datetime, aiohttp
from concurrent.futures import ThreadPoolExecutor
from backend.app.db.session import SessionLocal
from backend.app.db.helpers.audit import audit_received, audit_processed, audit_failed

router = APIRouter()


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(
    request: Request,
    x_twilio_signature: str | None = Header(default=None)
):
    """
    ✅ Handles incoming WhatsApp messages from Twilio.
    ✅ Validates signature.
    ✅ Extracts and standardizes message.
    ✅ Forwards message to ORKO ingestion route asynchronously.
    ✅ Sends auto-reply in background.
    ✅ Logs audit trail for message flow.
    """
    db = SessionLocal()
    audit_id = None

    try:
        # 1️⃣ Load environment variables
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        from_whatsapp = os.getenv("TWILIO_WHATSAPP_FROM")

        if not all([auth_token, account_sid, from_whatsapp]):
            raise HTTPException(status_code=500, detail="Missing Twilio environment variables")

        # 2️⃣ Parse the form data sent by Twilio
        try:
            form = await request.form()
            form_dict = dict(form)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid form payload: {e}")

        # 3️⃣ Validate Twilio signature
        validator = RequestValidator(auth_token)
        url = str(request.url)

        # 🧩 Log audit entry immediately (before validation)
        msg_id = form_dict.get("MessageSid", "unknown")
        audit_id = audit_received(db, source="whatsapp", msg_id=msg_id, org_id=1)
        print(f"🧩 [AUDIT] Logged audit_id={audit_id}")

        if not x_twilio_signature:
            if audit_id:
                audit_failed(db, audit_id, "Missing X-Twilio-Signature header")
            raise HTTPException(status_code=400, detail="Missing X-Twilio-Signature header")

        is_valid = validator.validate(url, form_dict, x_twilio_signature)
        if not is_valid:
            if audit_id:
                audit_failed(db, audit_id, "Invalid Twilio signature")
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

        # 4️⃣ Extract and standardize
        from_number = form_dict.get("From", "")
        sender = from_number.replace("whatsapp:", "").strip() if from_number else "unknown"
        content = (form_dict.get("Body") or "").strip()
        attachments = []
        num_media = int(form_dict.get("NumMedia", "0") or "0")

        for i in range(num_media):
            media_url = form_dict.get(f"MediaUrl{i}")
            media_type = form_dict.get(f"MediaContentType{i}")
            if media_url:
                attachments.append({"url": media_url, "type": media_type})

        timestamp_value = form_dict.get("Timestamp") or datetime.datetime.utcnow().isoformat()

        unified_msg = {
            "source": "whatsapp",
            "sender": sender,
            "content": content,
            "attachments": attachments,
            "timestamp": timestamp_value,
        }

        print(f"👤 sender = {sender}")
        print(f"💬 content = {content!r}")
        print(f"📎 attachments = {attachments}")
        print("🧩 unified_msg =", json.dumps(unified_msg, indent=2))

        # 5️⃣ Respond immediately to Twilio to prevent timeout
        asyncio.create_task(
            handle_ingestion_and_reply(
                unified_msg,
                account_sid,
                auth_token,
                from_whatsapp,
                from_number,
                content
            )
        )

        # 🧩 Mark audit as processed once background task scheduled
        if audit_id:
            audit_processed(db, audit_id)

        return JSONResponse({"status": "ok"})

    except Exception as e:
        # ⚠️ Audit failure tracking
        if audit_id:
            audit_failed(db, audit_id, str(e))
        raise

    finally:
        db.close()


# --- Background handler ---
async def handle_ingestion_and_reply(unified_msg, account_sid, auth_token, from_whatsapp, from_number, content):
    """Handle forwarding and Twilio reply asynchronously in background."""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": "Bearer supersecret123"}
            async with session.post("http://127.0.0.1:8000/ingest/message", json=unified_msg, headers=headers) as resp:
                print(f"📤 Background: forwarded to ingestion ({resp.status})")
    except Exception as e:
        print(f"⚠️ Background ingestion failed: {e}")

    try:
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)

        def send_twilio():
            client = Client(account_sid, auth_token)
            reply_text = f"Hi 👋 this is ORKO AI.\nYou said: '{content}'"
            client.messages.create(from_=from_whatsapp, to=from_number, body=reply_text)
            print(f"✅ Background auto-reply sent to {from_number}")

        await loop.run_in_executor(executor, send_twilio)
    except Exception as e:
        print(f"❌ Background Twilio reply failed: {e}")
