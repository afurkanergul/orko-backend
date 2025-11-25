# app/integrations/sharepoint_integration.py
import os
import msal
import requests

def _required_env(var):
    val = os.getenv(var)
    if not val:
        raise EnvironmentError(f"Missing {var} in .env.local")
    return val

def list_sharepoint_files():
    """
    Connects to Microsoft Graph API and lists files in your OneDrive/SharePoint root
    using application-only (client credentials) authentication.
    """
    MS_CLIENT_ID = _required_env("MS_CLIENT_ID")
    MS_TENANT_ID = _required_env("MS_TENANT_ID")
    MS_CLIENT_SECRET = _required_env("MS_CLIENT_SECRET")

    # 1️⃣ Authenticate using MSAL
    app = msal.ConfidentialClientApplication(
        client_id=MS_CLIENT_ID,
        client_credential=MS_CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{MS_TENANT_ID}"
    )

    token_result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in token_result:
        raise RuntimeError(f"Could not acquire token: {token_result}")

    token = token_result["access_token"]

    # 2️⃣ List available drives (works for app-only mode)
    drives_resp = requests.get(
        "https://graph.microsoft.com/v1.0/drives",
        headers={"Authorization": f"Bearer {token}"}
    )
    if drives_resp.status_code != 200:
        raise RuntimeError(f"Failed to list drives: {drives_resp.text}")

    drives = drives_resp.json().get("value", [])
    if not drives:
        raise RuntimeError("No drives found. Check app permissions (Files.Read.All, Sites.Read.All).")

    first_drive_id = drives[0]["id"]
    first_drive_name = drives[0].get("name", "Unnamed Drive")
    print(f"✅ Found drive: {first_drive_name} ({first_drive_id})")

    # 3️⃣ List root files in that drive
    files_url = f"https://graph.microsoft.com/v1.0/drives/{first_drive_id}/root/children"
    files_resp = requests.get(files_url, headers={"Authorization": f"Bearer {token}"})
    if files_resp.status_code != 200:
        raise RuntimeError(f"Graph call failed ({files_resp.status_code}): {files_resp.text}")

    data = files_resp.json().get("value", [])
    if not data:
        print("⚠️  No files found in the drive root.")
    else:
        for item in data:
            print(f"📄 {item['name']} — {item['id']}")
    return data
