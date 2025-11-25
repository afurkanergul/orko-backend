# backend/app/routers/telegram.py
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import datetime, httpx
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.db.helpers.audit import audit_received, audit_processed, audit_failed

router = APIRouter()

# ==============================================================  
# 💬 Background Helpers  
# ==============================================================  
async def _send_autoreply(chat_id: int, text: str):
    """Sends a polite confirmation back to the Telegram user."""
    token = settings.telegram_bot_token
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    async with httpx.AsyncClient(timeout=5) as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})


async def _save_message_background(payload: dict):
    """Simulated queue: saves message in the background."""
    from backend.app.routes.ingest import save_message_to_db
    await save_message_to_db(payload)


# ==============================================================  
# 🧠 Parsing Helpers  
# ==============================================================  
def extract_text(update: dict) -> str:
    msg = update.get("message") or update.get("edited_message") or {}
    return (msg.get("text") or "").strip()


def extract_chat_id(update: dict):
    msg = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat") or {}
    return chat.get("id")


def extract_sender(update: dict) -> str:
    msg = update.get("message") or update.get("edited_message") or {}
    frm = msg.get("from") or {}
    name = frm.get("first_name", "") or frm.get("username", "")
    return name.strip() or str(frm.get("id", ""))


def extract_timestamp() -> str:
    """Universal UTC timestamp."""
    return datetime.datetime.utcnow().isoformat()


# ==============================================================  
# 🚀 Main Secure Webhook with Background & Parsing  
# ==============================================================  
@router.post("/telegram/webhook")
async def telegram_webhook_with_background(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: str | None = Header(default=None)
):
    """
    ✅ Secure webhook + background save + autoreply + audit trail
    """
    # --- 🧩 Added for audit ---
    from backend.app.db.session import SessionLocal
    from backend.app.db.helpers.audit import audit_received, audit_processed, audit_failed
    db = SessionLocal()
    audit_id = None
    # --------------------------

    try:
        # --- 1️⃣ Validate secret token ---
        expected = settings.telegram_webhook_secret
        if not expected:
            raise HTTPException(status_code=500, detail="Missing TELEGRAM_WEBHOOK_SECRET in env")
        if x_telegram_bot_api_secret_token != expected:
            raise HTTPException(status_code=401, detail="Unauthorized: bad secret header")

        # --- 2️⃣ Parse the incoming JSON ---
        try:
            update = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # --- 🧩 Log audit entry right after JSON parse ---
        msg_id = str(update.get("update_id", "unknown"))
        audit_id = audit_received(db, source="telegram", msg_id=msg_id, org_id=1)
        print(f"🧩 [AUDIT] Logged audit_id={audit_id}")

        # --- 3️⃣ Extract clean fields ---
        chat_id = extract_chat_id(update)
        text = extract_text(update)
        sender = extract_sender(update)
        timestamp = extract_timestamp()

        payload = {
            "source": "telegram",
            "chat_id": chat_id,
            "sender": sender,
            "text": text,
            "timestamp": timestamp,
            "raw": update,  # kept for debugging
        }

        print("🤖 [TELEGRAM] Message received:", payload)

        # --- 4️⃣ Save + autoreply asynchronously ---
        background_tasks.add_task(_save_message_background, payload)

        if chat_id:
            background_tasks.add_task(_send_autoreply, chat_id, "Message received ✅")

        # --- 🧩 Mark audit as processed once queued ---
        if audit_id:
            audit_processed(db, audit_id)

        # --- 5️⃣ Respond immediately to Telegram ---
        return JSONResponse({"ok": True})

    except Exception as e:
        # --- ⚠️ Update audit on failure ---
        if audit_id:
            audit_failed(db, audit_id, str(e))
        raise

    finally:
        # --- Always close DB session ---
        db.close()
