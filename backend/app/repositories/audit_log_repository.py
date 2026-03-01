from abc import ABC, abstractmethod

from app.domain.audit_log import AuditLog


class AuditLogRepository(ABC):

    @abstractmethod
    def save(self, audit_log: AuditLog) -> AuditLog:
        pass
