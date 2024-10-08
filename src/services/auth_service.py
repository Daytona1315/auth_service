from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import models
from src.database.engine import get_async_session
from src.schemas.auth_schema import (
    User, Token, UserCreate,
)
from src.settings import settings


class AuthService:
    """The service for registration and authentication of users."""

    oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/sign-in')

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_schema)) -> User:
        return AuthService.validate_token(token)

    # OAUTH2 METHODS ----------
    @classmethod
    def verify_password(cls, raw_password: str, hash_password: str) -> bool:
        return bcrypt.verify(raw_password, hash_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def validate_token(cls, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='Cannot validate token'
            )

        user_data = payload.get('user')

        try:
            user = User.model_validate(user_data)
        except ValidationError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='Cannot validate token'
            )

        return user

    @classmethod
    def create_token(cls, user: User, ) -> Token:
        user_data = User.model_validate(user)
        now = datetime.now()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(settings.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.model_dump(),
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        return Token(access_token=token)

    # CREATION OF ASYNC DATABASE SESSION ----------
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    # USER REGISTRATION METHOD ----------
    async def register_new_user(self, user_data: UserCreate) -> Token:
        async with (self.session.begin()):
            try:

                # Adding new user to db and return id for further operations
                user_stmt = insert(models.User).values(
                    username=user_data.username,
                    email=user_data.email
                ).returning(models.User.id)
                user_result = await self.session.execute(user_stmt)
                user_id = user_result.scalar()

                # Adding credentials to db
                credentials_stmt = insert(models.CredentialsLocal).values(
                    user_id=user_id,
                    email=user_data.email,
                    hashed_password=self.hash_password(user_data.password)
                )
                await self.session.execute(credentials_stmt)

            # Handle errors
            except IntegrityError:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail="Failed to create user and credentials.")

        # Create token
        user = User(
            email=user_data.email,
            username=user_data.username,
            id=user_id
        )
        token = self.create_token(user)
        return token

    # USER AUTHENTICATION METHOD ----------
    async def authenticate_user(self, password: str, email: str,) -> Token:
        async with self.session.begin():
            try:

                # Search for user
                user_stmt = select(models.CredentialsLocal).filter_by(
                    email=email
                )
                user_result = await self.session.execute(user_stmt)
                user = user_result.scalar()

                # Handle exception if user doesn't exist
                if not user:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

                # Fetching for user's hashed password
                password_stmt = select(models.CredentialsLocal.hashed_password).filter_by(
                    email=email
                )
                password_result = await self.session.execute(password_stmt)
                hashed_password = password_result.scalar()
                if not hashed_password:
                    raise HTTPException(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Something went wrong",
                    )

