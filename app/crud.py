import base64
import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import asc
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.email_utils import EmailNotifier
from app.models import Document, Lead, LeadStatus


logger = logging.getLogger(__name__)


# TODO: Consolidate lead cruds into class to be more organized
def get_leads(
    db: Session,
    status: Optional[models.LeadStatus] = None,
    assigned_to_user: Optional[models.User] = None
):
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)

    if assigned_to_user:
        query = query.filter(Lead.assigned_to == assigned_to_user)

    # Add sort parameter later
    query = query.order_by(asc(Lead.created_at))
    return query.all()


def get_lead(db: Session, lead_id: str) -> dict:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        # TODO: might want to reconsider this. Maybe raise something different so that
        # this isn't conceptually coupled with being called within a route. Running out of
        # time though so keeping it as a first pass.
        raise HTTPException(status_code=404, detail="Lead not found")

    if not lead.resume or not os.path.exists(lead.resume.local_path):
        raise HTTPException(status_code=404, detail="Resume file not found")

    try:
        with open(lead.resume.local_path, "rb") as f:
            resume_contents = f.read()
        resume_b64 = base64.b64encode(resume_contents).decode("utf-8")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read resume file")

    return {
        "id": lead.id,
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "status": lead.status,
        "assigned_to_id": lead.assigned_to_id,
        "resume_id": lead.resume_id,
        "resume_b64": resume_b64
    }

def update_lead_status(db: Session, lead_id: uuid.UUID, new_status: LeadStatus):
    lead = db.query(models.Lead).filter(models.Lead.id == str(lead_id)).first()
    if lead:
        lead.status = new_status
        db.commit()
        return lead
    return None


class DocumentCrud:
    UPLOAD_DIR = "uploads/resumes"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    def __init__(self, db: Session):
        self.db = db

    def _persist_file(self, local_path: str, document_file: UploadFile) -> None:
        """ Save file locally for now. In production, this should be replaced with
        S3 integration
        """
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(document_file.file, buffer)


    def clean_up(self, document: Document):
        """Helper function to clean up persisted file in the case of a transaction rollback"""

        local_path = document.local_path
        if os.path.exists(local_path):
            os.remove(local_path)

    def create(self, document_file: UploadFile) -> Document:
        document_id = str(uuid.uuid4())
        ext = os.path.splitext(document_file.filename)[-1]

        local_filename = f"{document_id}{ext}"
        local_path = os.path.join(self.UPLOAD_DIR, local_filename)

        self._persist_file(local_path, document_file)

        document = Document(
            id=document_id,
            original_filename=document_file.filename,
            local_path=local_path,
            uploaded_at=datetime.utcnow(),
            document_type="resume"
        )
        self.db.add(document)
        return document


class LeadCrud:
    def __init__(self, db: Session):
        self.db = db

    def _get_assignee_for_new_lead(self, email: str) -> Optional[models.User]:
        # For now, just randomly choose a User that can_intake.
        # TODO: Make this more sophisticated later by assigning to User with the
        # least number of pending leads. Or maybe implement some round robin system
        random_assignee = self.db.query(
            models.User
        ).filter(
            models.User.can_intake == True
        ).order_by(
            func.random()
        ).first()

        if not random_assignee:
            logger.error(f'No users can intake lead with email {email}')
        else:
            return random_assignee

    def _notify_on_create(self, lead):
        notifier = EmailNotifier(self.db)
        notifier.send_new_lead_email_notification(lead)

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        resume_id: uuid.UUID
    ) -> Lead:
        assignee = self._get_assignee_for_new_lead(email)
        lead = Lead(
            first_name=first_name,
            last_name=last_name,
            email=email,
            resume_id=resume_id,
            status="PENDING",
            assigned_to=assignee
        )
        self.db.add(lead)

        self._notify_on_create(lead)
        return lead
