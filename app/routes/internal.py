import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, crud
from app.auth import authenticate_user, create_access_token, get_current_user
from app.database import get_db
from app.models import LeadStatus

router = APIRouter()


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/leads", response_model=list[schemas.LeadSummary])
def get_leads(
    db: Session = Depends(get_db),
    status: Optional[LeadStatus] = Query(None),
    assigned_to_me: Optional[bool] = Query(None),
    current_user=Depends(get_current_user)
):
    assigned_to_user = None
    if assigned_to_me:
        assigned_to_user = current_user
    return crud.get_leads(db, status=status, assigned_to_user=assigned_to_user)


@router.get("/leads/{lead_id}", response_model=schemas.LeadDetail)
def get_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud.get_lead(db, lead_id)


@router.patch("/leads/{lead_id}", response_model=schemas.LeadSummary)
def update_lead_status(
    lead_id: uuid.UUID,
    status: LeadStatus,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # TODO: Maybe add permission check in case we want to limit who can update which lead.
    # Without product guidance, I'll just leave it so that anyone can update any lead
    lead = crud.update_lead_status(db, lead_id, status)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
