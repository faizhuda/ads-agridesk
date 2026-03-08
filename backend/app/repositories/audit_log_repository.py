from sqlalchemy.orm import Session

from app.models.audit_log import AuditLogModel


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: AuditLogModel) -> AuditLogModel:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_target(self, target_type: str, target_id: int):
        return (
            self.db.query(AuditLogModel)
            .filter(
                AuditLogModel.target_type == target_type,
                AuditLogModel.target_id == target_id,
            )
            .order_by(AuditLogModel.created_at.desc())
            .all()
        )
