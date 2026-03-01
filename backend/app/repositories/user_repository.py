from abc import ABC, abstractmethod
from typing import List

from app.domain.user import User


class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_email(self, email: str):
        pass

    @abstractmethod
    def find_by_id(self, user_id: int):
        pass

    @abstractmethod
    def find_by_ids(self, user_ids: List[int]) -> List[User]:
        pass

    @abstractmethod
    def find_by_role(self, role: str) -> List[User]:
        pass