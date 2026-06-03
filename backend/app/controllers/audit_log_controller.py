from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.enums import UserRole
from app.schemas.audit_log_schema import PaginatedAuditLogResponse
from app.services.audit_log_service import AuditLogService
from app.utils.dependencies import get_current_user, require_role

router = APIRouter()

@router.get(
    "",
    response_model=PaginatedAuditLogResponse,
    dependencies=[Depends(require_role(UserRole.ADMIN))]
)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve system audit logs. Only accessible by ADMIN."""
    items, total = AuditLogService(db).get_enriched_logs(skip=skip, limit=limit)
    return PaginatedAuditLogResponse(items=items, total=total, skip=skip, limit=limit)
