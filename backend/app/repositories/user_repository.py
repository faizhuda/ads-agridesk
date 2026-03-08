from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_nim(self, nim: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.nim == nim).first()

    def get_by_nip(self, nip: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.nip == nip).first()

    def get_all(self) -> List[UserModel]:
        return self.db.query(UserModel).all()

    def get_lecturers(self) -> List[UserModel]:
        from app.domain.enums import UserRole
        return self.db.query(UserModel).filter(UserModel.role == UserRole.DOSEN).all()

    def search_lecturers(self, keyword: str, limit: int = 10) -> List[UserModel]:
        from app.domain.enums import UserRole

        query = self.db.query(UserModel).filter(UserModel.role == UserRole.DOSEN)
        if keyword.strip():
            pattern = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    UserModel.name.ilike(pattern),
                    UserModel.nip.ilike(pattern),
                )
            )
        return query.order_by(UserModel.name.asc()).limit(limit).all()

    def update(self, user: UserModel) -> UserModel:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
