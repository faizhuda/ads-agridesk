from typing import Any

from app.domain.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:

    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    def log_event(
        self,
        event_name: str,
        actor_id: int | None,
        actor_role: str | None,
        target_type: str | None,
        target_id: str | None,
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
        status: str = "SUCCESS",
    ) -> AuditLog:
        audit_log = AuditLog(
            event_name=event_name,
            actor_id=actor_id,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            status=status,
            metadata=metadata,
            ip_address=ip_address,
        )
        return self.repository.save(audit_log)
