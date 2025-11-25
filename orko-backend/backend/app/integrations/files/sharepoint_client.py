from backend.app.core.vault_manager import load_token, save_token
def fetch_sharepoint_delta():
    """
    Checks the vault for SharePoint credentials,
    and prepares to fetch file delta changes.
    """

    creds = load_token("sharepoint")

    if not creds:
        print("⚠️ No SharePoint token found in vault yet.")
        return []

    print("🔑 Loaded SharePoint token from vault.")

    dummy_change = {
        "provider": "sharepoint",
        "remote_id": "xyz789",
        "name": "contracts2025.docx",
        "modified_at": "2025-11-04T20:46:00Z",
        "owner": "ahmet@greenfield.com",
    }

    return [dummy_change]
