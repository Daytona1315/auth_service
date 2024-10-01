from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import models
from src.database.engine import get_async_session
from src.database.models import User
from src.schemas.auth_schema import User, Token, UserCreate
from src.settings import settings


class AuthService:

    oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/sign-in')

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_schema)) -> User:
        return AuthService.validate_token(token)

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
                detail='Cannot validate token')

        return user

    @classmethod
    def create_token(cls, user: User, ) -> Token | dict:
        user_data = User.model_validate(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(settings.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.model_dump(),
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return Token(access_token=token)

    # CREATION OF ASYNC DATABASE SESSION
    def __init__(self, async_session: AsyncSession = Depends(get_async_session)):
        self.async_session = async_session

    # USER REGISTRATION METHOD
    async def register_new_user(self, user_data: UserCreate) -> Token | HTTPException:
        async with self.async_session as session:
            table = await session.execute(select(models.User).filter_by(email=user_data.email))
            user = table.scalar()

            if user:
                return HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="E-mail already exist",
                )

            new_user = models.User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=self.hash_password(user_data.password)
            )

            try:
                session.add(new_user)
                await session.commit()
            except Exception:
                await session.rollback()
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong",
                )
            return self.create_token(user)

    # USER AUTHENTICATION METHOD
    async def authenticate_user(self, username: str, password: str) -> Token | HTTPException:
        async with self.async_session as session:
            result = await session.execute(select(models.User).filter_by(username=username))
            user = result.scalar()

            if not user:
                return HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            result = await session.execute(
                select(models.User.hashed_password).filter_by(id=user.id)
            )

            hashed_password = result.scalar()

            if not hashed_password:
                return HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="Password is incorrect",
                )

            if not self.verify_password(password, hashed_password):
                return HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Cannot validate credentials"
                )
            return self.create_token(user)
