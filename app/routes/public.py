from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

router = APIRouter()



@router.get("/")
async def root():
    return {"message": "Hello public"}


@router.post(
    "/leads",
    response_model=schemas.LeadSummary,
    status_code=201,
    responses={
        500: {'model': schemas.ErrorResponse, 'description': 'Failed to upload resume and create lead'},
    }

)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    document_crud = crud.DocumentCrud(db)
    lead_crud = crud.LeadCrud(db)
    document = None
    try:
        # start a transaction
        with db.begin():
            # Create the document
            document = document_crud.create(document_file=resume_file)

            # create the lead
            lead = lead_crud.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                resume_id=document.id
            )

        db.refresh(lead)
    except Exception:
        if document:
            document_crud.clean_up(document)
        raise
        raise HTTPException(status_code=500, detail="Failed to create lead and document")

    return lead
