from typing import List

from sqlalchemy.orm import Session

from app.database.models.user_model import UserModel
from app.repositories.user_repository import UserRepository
from app.domain.user import User, UserRole


class PostgresUserRepository(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User):
        db_user = UserModel(
            name=user.name,
            email=user.email,
            nim=user.nim,
            nip=user.nip,
            password_hash=user.password_hash,
            role=user.role.value
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        user.user_id = db_user.id
        return user

    def find_by_email(self, email: str):
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()

        if not db_user:
            return None

        return self._to_domain(db_user)

    def find_by_id(self, user_id: int):
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()

        if not db_user:
            return None

        return self._to_domain(db_user)

    def find_by_ids(self, user_ids: List[int]) -> List[User]:
        if not user_ids:
            return []
        rows = self.db.query(UserModel).filter(UserModel.id.in_(user_ids)).all()
        return [self._to_domain(r) for r in rows]

    def find_by_role(self, role: str) -> List[User]:
        rows = (
            self.db.query(UserModel)
            .filter(UserModel.role == role)
            .order_by(UserModel.name)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def _to_domain(self, db_user: UserModel) -> User:
        return User(
            user_id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            password_hash=db_user.password_hash,
            role=UserRole(db_user.role),
            nim=db_user.nim,
            nip=db_user.nip,
        )