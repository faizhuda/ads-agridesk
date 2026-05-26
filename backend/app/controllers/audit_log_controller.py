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
    """
    Retrieve system audit logs. Only accessible by ADMIN.
    """
    audit_service = AuditLogService(db)
    logs, total = audit_service.get_logs(skip=skip, limit=limit)
    
    from app.schemas.audit_log_schema import AuditLogResponse
    from app.models.user import UserModel
    from app.models.surat import SuratModel

    actor_ids = {log.actor_id for log in logs if log.actor_id}
    surat_ids = {log.target_id for log in logs if log.target_id and log.target_type and "surat" in log.target_type.lower()}
    
    user_names = {}
    if actor_ids:
        users = db.query(UserModel.id, UserModel.name).filter(UserModel.id.in_(actor_ids)).all()
        user_names = {u.id: u.name for u in users}
        
    surat_names = {}
    if surat_ids:
        surats = db.query(SuratModel.id, SuratModel.jenis).filter(SuratModel.id.in_(surat_ids)).all()
        surat_names = {s.id: s.jenis for s in surats}

    items = [
        AuditLogResponse(
            id=log.id,
            event_name=log.event_name,
            actor_id=log.actor_id,
            actor_role=log.actor_role,
            actor_name=user_names.get(log.actor_id),
            target_type=log.target_type,
            target_id=log.target_id,
            target_name=surat_names.get(log.target_id) if log.target_type and "surat" in log.target_type.lower() else None,
            status=log.status,
            metadata_json=log.metadata_json,
            ip_address=log.ip_address,
            created_at=log.created_at
        )
        for log in logs
    ]
    
    return PaginatedAuditLogResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )
