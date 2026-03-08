from typing import Optional

from sqlalchemy.orm import Session

from app.models.letter_template import LetterTemplateModel


class LetterTemplateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_internal_templates(self) -> list[LetterTemplateModel]:
        return (
            self.db.query(LetterTemplateModel)
            .order_by(LetterTemplateModel.id.asc())
            .all()
        )

    def get_by_name(self, name: str) -> Optional[LetterTemplateModel]:
        return (
            self.db.query(LetterTemplateModel)
            .filter(LetterTemplateModel.name == name)
            .first()
        )
