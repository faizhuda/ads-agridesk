from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.verification_schema import VerificationResponse
from app.services.verification_service import VerificationService

router = APIRouter(prefix="/verify", tags=["Verification"])


@router.get("/{document_hash}", response_model=VerificationResponse)
def verify_document(document_hash: str, db: Session = Depends(get_db)):
    service = VerificationService(db)
    return service.verify_document(document_hash)
