from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import engine
from app.db import models

db = Session(bind=engine)

# ------------------------------------------------------------
# ✅ 1. Create baseline Org
# ------------------------------------------------------------
org = models.Org(
    name="Greenfield Commodities",
    domain="greenfield.ai",
    plan="pro"
)
db.add(org)
db.commit()
db.refresh(org)
print(f"🏢 Created org: {org.name} (ID={org.id})")

# ------------------------------------------------------------
# ✅ 2. Create Admin User (role = 'admin')
# ------------------------------------------------------------
admin = models.User(
    org_id=org.id,
    name="System Admin",
    email="admin@greenfield.ai",
    hashed_password="admin123",
    role="admin",
)
db.add(admin)
db.commit()
db.refresh(admin)
print(f"👤 Created admin user: {admin.email}")

# ------------------------------------------------------------
# ✅ 3. Optional seed automation example
# ------------------------------------------------------------
automation = models.Automation(
    user_id=admin.id,
    name="Welcome Message",
    trigger="user.signup",
    action="send_email",
    config={"subject": "Welcome to Greenfield", "template": "welcome.html"},
)
db.add(automation)
db.commit()
print("⚙️  Added example automation.")

db.close()
print("🌱 Seeding complete.")
