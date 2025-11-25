from pydantic import BaseModel

class CurrentUser(BaseModel):
    id: str
    email: str | None = None
    role: str  # "viewer" | "operator" | "admin"
