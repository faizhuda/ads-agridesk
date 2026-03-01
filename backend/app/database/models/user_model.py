from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    nim = Column(String, unique=True, index=True, nullable=True)
    nip = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)