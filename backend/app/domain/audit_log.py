from datetime import datetime, timezone
from typing import Any


class AuditLog:

    def __init__(
        self,
        event_name: str,
        actor_id: int | None,
        actor_role: str | None,
        target_type: str | None,
        target_id: str | None,
        status: str = "SUCCESS",
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ):
        self.audit_log_id = None
        self.event_name = event_name
        self.actor_id = actor_id
        self.actor_role = actor_role
        self.target_type = target_type
        self.target_id = target_id
        self.status = status
        self.metadata = metadata or {}
        self.ip_address = ip_address
        self.created_at = datetime.now(timezone.utc)
