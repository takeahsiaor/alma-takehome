from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr
from enum import Enum

from app.models import LeadStatus


class ErrorResponse(BaseModel):
    detail: str


class LeadSummary(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_id: UUID
    assigned_to_id: Optional[UUID]
    status: LeadStatus

    class Config:
        orm_mode = True


class LeadDetail(LeadSummary):
    resume_b64: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class TokenRequest(BaseModel):
    username: str
    password: str
