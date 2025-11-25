import sys, pathlib, re
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))  # ✅ adds project root dynamically

from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.integrations.email.outlook_client import fetch_outlook_emails
from backend.app.core.vault_manager import load_token



def detect_provider(email: str) -> str:
    """
    Detect the provider based on email domain.
    """
    email = email.lower()
    if re.search(r"@(gmail\.com|googlemail\.com)$", email):
        return "gmail"
    if re.search(r"@(outlook\.com|hotmail\.com|live\.com|office365\.com|microsoft\.com)$", email):
        return "outlook"
    return "unknown"


def fetch_user_emails(user_email: str = None, source: str = "all", limit: int = 10):
    """
    Unified email fetcher for ORKO AI.

    Modes:
    - If user_email is provided → auto-detect provider and fetch from that source.
    - If no email provided → use source param ("gmail", "outlook", or "all").
    - Uses secure vault tokens for authorization.
    """
    emails = []

    # 🧠 If a specific email is given, detect the provider automatically
    if user_email:
        provider = detect_provider(user_email)
        if provider == "unknown":
            return {"error": f"Unsupported or unknown domain for '{user_email}'"}

        # 🔐 Check if token exists in vault
        token = load_token(provider)
        if not token:
            return {
                "auth_required": True,
                "provider": provider,
                "next_step": f"/auth/{provider}",
                "message": f"Authorization required for {provider.title()} account."
            }

        # ✅ If already authorized, fetch directly
        try:
            if provider == "gmail":
                gmail_emails = fetch_gmail_emails(limit)
                return {"provider": "gmail", "emails": gmail_emails}
            elif provider == "outlook":
                outlook_emails = fetch_outlook_emails(limit)
                return {"provider": "outlook", "emails": outlook_emails}
        except Exception as e:
            return {"provider": provider, "error": str(e)}

    # 🧩 If no email is provided → use “source” param logic
    if source.lower() in ["gmail", "all"]:
        try:
            gmail_token = load_token("gmail")
            if gmail_token:
                gmail_emails = fetch_gmail_emails(limit)
                emails.extend([{"source": "gmail", **e} for e in gmail_emails])
                print(f"📥 Retrieved {len(gmail_emails)} Gmail emails.")
            else:
                print("⚠️ Gmail not authorized or token missing.")
        except Exception as e:
            emails.append({"source": "gmail", "error": str(e)})

    if source.lower() in ["outlook", "all"]:
        try:
            outlook_token = load_token("outlook")
            if outlook_token:
                outlook_emails = fetch_outlook_emails(limit)
                emails.extend([{"source": "outlook", **e} for e in outlook_emails])
                print(f"📥 Retrieved {len(outlook_emails)} Outlook emails.")
            else:
                print("⚠️ Outlook not authorized or token missing.")
        except Exception as e:
            emails.append({"source": "outlook", "error": str(e)})

    # Return unified output
    return {
        "count": len(emails),
        "emails": emails
    }


if __name__ == "__main__":
    print("🔍 Fetching unified emails from all sources...\n")

    result = fetch_user_emails(source="all", limit=5)

    if isinstance(result, dict) and "emails" in result and result["emails"]:
        print(f"✅ Total emails retrieved: {result['count']}\n")
        for i, mail in enumerate(result["emails"], start=1):
            print(f"{i:02d}. [{mail['source'].upper()}] {mail['subject']} — {mail.get('from')}")
    elif "auth_required" in result:
        print(f"🔒 {result['message']}")
    else:
        print("❌ No emails retrieved.")
