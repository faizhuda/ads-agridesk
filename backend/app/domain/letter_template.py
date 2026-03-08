from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LetterTemplate:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    template_path: str = ""
    required_fields: List[str] = field(default_factory=list)

    def get_template(self) -> str:
        return self.template_path

    def validate_fields(self, provided_fields: dict) -> List[str]:
        missing = [f for f in self.required_fields if f not in provided_fields]
        return missing
