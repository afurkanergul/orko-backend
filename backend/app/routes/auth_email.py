from fastapi import APIRouter
from backend.app.integrations.email.gmail_client import fetch_gmail_emails
from backend.app.integrations.email.outlook_client import fetch_outlook_emails

# Define the router for email-related routes
router = APIRouter(prefix="/emails", tags=["Email Integration"])

# Gmail endpoint
@router.get("/gmail")
def get_gmail_emails(limit: int = 10):
    """
    Connect to Gmail and fetch latest email subjects.
    """
    try:
        emails = fetch_gmail_emails(limit)
        return {"source": "gmail", "count": len(emails), "emails": emails}
    except Exception as e:
        return {"error": str(e)}

# Outlook endpoint
@router.get("/outlook")
def get_outlook_emails(limit: int = 10):
    """
    Connect to Outlook (Microsoft 365) and fetch latest email subjects.
    """
    try:
        emails = fetch_outlook_emails(limit)
        return {"source": "outlook", "count": len(emails), "emails": emails}
    except Exception as e:
        return {"error": str(e)}
