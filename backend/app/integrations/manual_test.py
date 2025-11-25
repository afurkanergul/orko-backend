# app/integrations/manual_test.py
from app.integrations.integration_manager import connect_user_drive

if __name__ == "__main__":
    # 👇 Use your Microsoft 365 work email so ORKO connects to SharePoint/OneDrive
    test_email = "ae@greenfield-commodities.com"

    print("Starting test for:", test_email)
    print("🔗 Detecting account type and initializing connection...\n")

    try:
        # Try connecting using whichever integration matches the domain
        items = connect_user_drive(test_email)

        print("\n✅ Received items:")
        if items:
            for it in items[:10]:
                # Google returns dicts with 'name'/'id'; Microsoft Graph returns similar keys
                name = it.get("name") or it.get("title")
                fid = it.get("id")
                print(f"- {name} — {fid}")
        else:
            print("(no items returned — token ok, but no visible files or permissions limited)")
    except Exception as e:
        print("❌ Error during integration test:")
        print(e)

    print("\nTest complete.")
