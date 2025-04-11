import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    # TODO: Migrate this to a Role
    can_intake = Column(Boolean, nullable=False, default=True)

# Maybe add a Role model here in the future for Role-based user permissions


class LeadStatus(str, enum.Enum):
    pending = "PENDING"
    reached_out = "REACHED_OUT"


class DocumentType(str, enum.Enum):
    resume = "RESUME"


class Lead(Base):
    __tablename__ = "leads"

    RESUME_S3_BUCKET = 'alma-takehome-resume-bucket'

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    # String type in the db but will enforce that the statuses conform to specific ones via python enum
    status = Column(String, default=LeadStatus.pending)

    resume_id = Column(String, ForeignKey("documents.id"), nullable=False)
    resume = relationship("Document", uselist=False)

    assigned_to_id = Column(String, ForeignKey('users.id'), nullable=True)
    assigned_to = relationship("User", uselist=False)


class Document(Base):
    __tablename__ = "documents"

    original_filename = Column(String, nullable=False)
    # For the purposes of this exercise, we will use local resume path but in a production environment,
    # we would store the resume in S3 or other equivalent
    local_path = Column(String, nullable=False)
    s3_key = Column(String, nullable=True)
    document_type = Column(String, nullable=False, default=DocumentType.resume)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class EmailNotification(Base):
    """Consider making this a general notification with a notification_type column
    instead of one specifically for email
    """
    __tablename__ = "email_notifications"

    # If we use an external email service, we can store external_id and external_service_name
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)

    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    lead = relationship("Lead", uselist=False)
