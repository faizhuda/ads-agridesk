"""
Centralised audit-logging service.

Replaces the duplicated ``_log_event`` helpers that previously existed in
both ``SuratService`` and ``SignatureService``.
"""

from sqlalchemy.orm import Session

from app.domain.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    """Single-responsibility service for recording audit trail events."""

    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditLogRepository(db)

    def log_event(
        self,
        event_name: str,
        actor_id: int,
        actor_role: str,
        target_type: str,
        target_id: int,
        status: str,
        metadata_json: str | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog.log_event(
            event_name=event_name,
            actor_id=actor_id,
            actor_role=actor_role,
            target_type=target_type,
            target_id=target_id,
            status=status,
            metadata_json=metadata_json,
            ip_address=ip_address,
        )
        return self.audit_repo.create(log)

    def get_logs(self, skip: int = 0, limit: int = 20) -> tuple[list[AuditLog], int]:
        logs = self.audit_repo.get_all(skip, limit)
        total = self.audit_repo.count_all()
        return logs, total

    def get_enriched_logs(self, skip: int = 0, limit: int = 20) -> tuple[list[dict], int]:
        """Return audit logs enriched with actor_name and target_name."""
        from app.models.user import UserModel
        from app.models.surat import SuratModel

        logs, total = self.get_logs(skip, limit)

        actor_ids = {log.actor_id for log in logs if log.actor_id}
        surat_ids = {
            log.target_id for log in logs
            if log.target_id and log.target_type and "surat" in log.target_type.lower()
        }

        user_names: dict = {}
        if actor_ids:
            rows = self.db.query(UserModel.id, UserModel.name).filter(UserModel.id.in_(actor_ids)).all()
            user_names = {u.id: u.name for u in rows}

        surat_names: dict = {}
        if surat_ids:
            rows = self.db.query(SuratModel.id, SuratModel.jenis).filter(SuratModel.id.in_(surat_ids)).all()
            surat_names = {s.id: s.jenis for s in rows}

        enriched = [
            {
                "id": log.id,
                "event_name": log.event_name,
                "actor_id": log.actor_id,
                "actor_role": log.actor_role,
                "actor_name": user_names.get(log.actor_id),
                "target_type": log.target_type,
                "target_id": log.target_id,
                "target_name": (
                    surat_names.get(log.target_id)
                    if log.target_type and "surat" in log.target_type.lower()
                    else None
                ),
                "status": log.status,
                "metadata_json": log.metadata_json,
                "ip_address": log.ip_address,
                "created_at": log.created_at,
            }
            for log in logs
        ]
        return enriched, total
