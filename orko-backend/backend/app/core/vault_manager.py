import json
import os
import time
from cryptography.fernet import Fernet
from pathlib import Path

# ✅ File paths
VAULT_PATH = Path(__file__).resolve().parent / "orko_vault.json"
KEY_PATH = Path(__file__).resolve().parent / "vault.key"

# ✅ Helper for encryption/decryption
def _get_fernet():
    if not KEY_PATH.exists():
        KEY_PATH.write_bytes(Fernet.generate_key())
    return Fernet(KEY_PATH.read_bytes())

# ✅ Save token (adds timestamp + optional client email)
def save_token(service: str, token_data: dict):
    f = _get_fernet()
    vault = json.loads(VAULT_PATH.read_text()) if VAULT_PATH.exists() else {}

    # Add metadata before saving
    token_data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # Try to capture the user's email if available
    if "client_email" not in token_data:
        if "email" in token_data:
            token_data["client_email"] = token_data["email"]
        elif "username" in token_data:
            token_data["client_email"] = token_data["username"]

    vault[service] = f.encrypt(json.dumps(token_data).encode()).decode()
    VAULT_PATH.write_text(json.dumps(vault, indent=2))

    print(f"✅ Token for '{service}' saved in vault at {token_data['saved_at']}")

# ✅ Load token safely
def load_token(service: str):
    if not VAULT_PATH.exists():
        return None

    f = _get_fernet()
    vault = json.loads(VAULT_PATH.read_text())

    if service not in vault:
        return None

    try:
        decrypted = f.decrypt(vault[service].encode()).decode()
        return json.loads(decrypted)
    except Exception as e:
        print(f"⚠️ Failed to read token for {service}: {e}")
        return None

# ✅ Optional: clear token manually
def clear_token(service: str):
    if not VAULT_PATH.exists():
        return
    vault = json.loads(VAULT_PATH.read_text())
    if service in vault:
        del vault[service]
        VAULT_PATH.write_text(json.dumps(vault, indent=2))
        print(f"🗑️ Token for '{service}' removed from vault.")
