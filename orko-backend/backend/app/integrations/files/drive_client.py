from backend.app.core.vault_manager import load_token, save_token
def fetch_drive_changes():
    """
    Checks the vault for Google Drive credentials,
    and prepares to fetch file changes.
    """

    creds = load_token("drive")

    # If no token is found yet, warn and exit quietly
    if not creds:
        print("⚠️ No Drive token found in vault yet.")
        return []

    # In the future: this is where you’ll call the real Drive API
    # using creds["access_token"], refresh tokens, etc.
    # For now, we’ll just pretend it worked.
    print("🔑 Loaded Drive token from vault.")

    # Simulate one fake file change so you can see it in logs
    dummy_change = {
        "provider": "drive",
        "remote_id": "abc123",
        "name": "budget2025.xlsx",
        "modified_at": "2025-11-04T20:45:00Z",
        "owner": "ahmet@greenfield.com",
    }

    # Later we’ll replace this with real Drive data
    return [dummy_change]
