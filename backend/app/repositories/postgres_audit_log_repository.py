import json
from sqlalchemy.orm import Session

from app.database.models.audit_log_model import AuditLogModel
from app.domain.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class PostgresAuditLogRepository(AuditLogRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, audit_log: AuditLog) -> AuditLog:
        db_audit_log = AuditLogModel(
            event_name=audit_log.event_name,
            actor_id=audit_log.actor_id,
            actor_role=audit_log.actor_role,
            target_type=audit_log.target_type,
            target_id=audit_log.target_id,
            status=audit_log.status,
            metadata_json=json.dumps(audit_log.metadata, ensure_ascii=False),
            ip_address=audit_log.ip_address,
        )
        self.db.add(db_audit_log)
        self.db.commit()
        self.db.refresh(db_audit_log)

        audit_log.audit_log_id = db_audit_log.id
        return audit_log
