from typing import List

from sqlalchemy import (
    String, Integer, Boolean, ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, default='user')
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    avatar: Mapped[str] = mapped_column(String, nullable=True, default='/path/to/default/avatar.jpg')
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    credentials_local: Mapped[List["CredentialsLocal"]] = relationship()
    credentials_google: Mapped[List["CredentialsGoogle"]] = relationship()


class CredentialsLocal(Base):
    __tablename__ = 'credentials_local'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped['User'] = relationship(back_populates='credentials_local')


class CredentialsGoogle(Base):
    __tablename__ = 'credentials_google'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped['User'] = relationship(back_populates='credentials_google')
