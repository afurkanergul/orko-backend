from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["overview"])

@router.get("/overview")
def get_overview():
    """
    Returns sample dashboard metrics for ORKO's 3 Brains.
    """
    return {
        "brains": {
            "knowledge": {"kpi": 128, "delta": "+3.2%"},
            "pattern": {"kpi": 42, "delta": "+1.8%"},
            "skill": {"kpi": 15, "delta": "+5.1%"},
        },
        "system": {"uptime": "99.9%", "status": "online"},
    }
