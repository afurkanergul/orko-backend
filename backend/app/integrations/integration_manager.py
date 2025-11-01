# app/integrations/integration_manager.py
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load .env.local from backend directory (so you don't need to move it)
env_path = Path(__file__).resolve().parent.parent.parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"⚠️  Warning: .env.local not found at {env_path}")

from app.integrations.drive_integration import list_drive_files
from app.integrations.sharepoint_integration import list_sharepoint_files


def detect_integration(email: str) -> str:
    """
    Decide which integration to use based on the email domain.
    """
    if "@" not in email:
        return "unknown"

    domain = email.split("@")[1].lower()

    # Define domain rules
    google_domains = ["gmail.com", "googlemail.com", "greenfield.com"]  # add your workspace domain here
    microsoft_keywords = ["outlook", "office365", "microsoft", "hotmail", "onmicrosoft"]

    if domain in google_domains:
        return "google"
    elif any(word in domain for word in microsoft_keywords):
        return "microsoft"
    else:
        return "unknown"


def connect_user_drive(email: str):
    """
    Route user email to the right integration stub (Google or Microsoft).
    """
    if email.endswith("@gmail.com") or email.endswith("@googlemail.com"):
        print(f"🔗 Detected Google account ({email}) — connecting to Google Drive...")
        from app.integrations.drive_integration import list_drive_files
        return list_drive_files()

    elif (
        email.endswith("@outlook.com")
        or email.endswith("@hotmail.com")
        or email.endswith("@live.com")
        or email.endswith("@greenfield-commodities.com")  # 👈 your company domain
    ):
        print(f"🔗 Detected Microsoft account ({email}) — connecting to Microsoft SharePoint...")
        from app.integrations.sharepoint_integration import list_sharepoint_files
        return list_sharepoint_files()

    else:
        raise ValueError(f"❌ Unsupported email domain: {email}")
