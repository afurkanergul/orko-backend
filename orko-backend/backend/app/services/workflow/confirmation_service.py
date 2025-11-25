from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

from backend.app.models.confirmation_request import ConfirmationRequest


class ConfirmationService:
    """
    Handles creation, retrieval, approval, and rejection of destructive action
    confirmation requests.
    """

    def create(
        self,
        db: Session,
        workflow_name: str,
        parameters: dict,
        user_id: str,
    ) -> ConfirmationRequest:

        req = ConfirmationRequest(
            id=str(uuid4()),
            workflow_name=workflow_name,
            parameters=parameters,
            user_id=user_id,
        )

        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    def get(self, db: Session, confirmation_id: str) -> ConfirmationRequest | None:
        return (
            db.query(ConfirmationRequest)
            .filter(ConfirmationRequest.id == confirmation_id)
            .first()
        )

    def approve(self, db: Session, confirmation_id: str) -> ConfirmationRequest | None:
        req = self.get(db, confirmation_id)
        if not req:
            return None

        req.approved = True
        req.rejected = False
        req.decided_at = datetime.utcnow()

        db.commit()
        db.refresh(req)
        return req

    def reject(self, db: Session, confirmation_id: str) -> ConfirmationRequest | None:
        req = self.get(db, confirmation_id)
        if not req:
            return None

        req.approved = False
        req.rejected = True
        req.decided_at = datetime.utcnow()

        db.commit()
        db.refresh(req)
        return req
