import sys, pathlib, os, json, requests, msal
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

from backend.app.core.vault_manager import save_token, load_token

# 📧 Microsoft App Config
CLIENT_ID = "f8ba6c8c-bb71-485e-a620-46f6f0d68748"
TENANT_ID = "3143a0c3-b69a-4333-bd2a-8d276a4803ef"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["Mail.Read", "User.Read"]
REDIRECT_URI = "http://localhost:8000"
TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# 📁 File paths
ROOT = pathlib.Path(__file__).resolve().parents[4]
TOKEN_FILE = ROOT / "backend/app/integrations/email/token_outlook.json"


def fetch_outlook_emails(limit=10):
    """Fetch latest Outlook emails using Microsoft Graph API with vault-based tokens."""
    token_data = load_token("outlook")
    access_token = None

    # 1️⃣ Use vault token if valid
    if token_data and "access_token" in token_data:
        access_token = token_data["access_token"]

    # 2️⃣ If expired → try refresh token
    if token_data and "refresh_token" in token_data:
        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        refreshed = app.acquire_token_by_refresh_token(token_data["refresh_token"], SCOPE)
        if "access_token" in refreshed:
            access_token = refreshed["access_token"]
            save_token("outlook", refreshed)
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(refreshed, f, indent=2)

    # 3️⃣ If still no token → start device flow
    if not access_token:
        app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        flow = app.initiate_device_flow(scopes=SCOPE)
        print(f"\n🔑 Go to {flow['verification_uri']} and enter code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            save_token("outlook", result)
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            access_token = result["access_token"]
        else:
            raise Exception("❌ Outlook authorization failed")

    # 4️⃣ Fetch emails
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://graph.microsoft.com/v1.0/me/messages?$top={limit}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"⚠️ Error fetching emails: {response.status_code} - {response.text}")
        return []

    data = response.json().get("value", [])
    emails = []

    # 5️⃣ Parse richer metadata (match Gmail structure)
    for e in data:
        emails.append({
            "source": "outlook",
            "from": e.get("from", {}).get("emailAddress", {}).get("address"),
            "to": (
                e.get("toRecipients", [{}])[0]
                .get("emailAddress", {})
                .get("address")
                if e.get("toRecipients")
                else None
            ),
            "subject": e.get("subject", "(no subject)"),
            "date": e.get("receivedDateTime"),
            "snippet": e.get("bodyPreview", ""),
            "unread": e.get("isRead") is False
        })

    return emails


if __name__ == "__main__":
    print("Connecting to Outlook...\n")
    try:
        emails = fetch_outlook_emails(10)
        if emails:
            print("✅ Outlook connected! Here are your latest subjects:\n")
            for i, e in enumerate(emails, start=1):
                print(f"{i:02d}. {e['subject']} — {e.get('from')}")
        else:
            print("❌ No emails found or connection failed.")
    except Exception as e:
        print("❌ Error:", e)
