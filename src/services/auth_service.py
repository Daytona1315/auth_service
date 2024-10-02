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
from src.schemas.auth_schema import User, Token, UserCreate, BaseUser
from src.settings import settings

'''
Задачи:
1. Поднять метод авторизации по той же схеме что и метод авторизации. (OK)
2. Решить проблему: регистрация проверяет только почту на уникальность,
должна проверять и имя пользователя тоже. (OK)
3. Наладить обработку ошибок в методах.
'''


class AuthService:
    """The service for registration and authentication of users."""

    oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/sign-in')

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_schema)) -> User:
        return AuthService.validate_token(token)

    # OAUTH2 METHODS----------
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
    def create_token(cls, user: User, ) -> Token:
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

    # CREATION OF ASYNC DATABASE SESSION ----------
    def __init__(self, async_session: AsyncSession = Depends(get_async_session)):
        self.async_session = async_session

    # USER REGISTRATION METHOD ----------
    async def register_new_user(self, user_data: UserCreate) -> Token:
        async with self.async_session as session:

            # Check email is already exist
            table = await session.execute(select(models.User).filter_by(email=user_data.email))
            user = table.scalar()
            if user:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="E-mail already exist",
                )
            # Check username is already exist
            table = await session.execute(select(models.User).filter_by(username=user_data.username))
            user = table.scalar()
            if user:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="Username already exist",
                )

            # Create a user in database
            new_user = models.User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=self.hash_password(user_data.password)
            )

            # Commiting changes
            try:
                session.add(new_user)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Something went wrong",
                )

            # Fetching user again (now he has an id) to create a token for him
            table = await session.execute(select(models.User).filter_by(email=user_data.email))
            user = table.scalar()
            token = self.create_token(user)

            return token

    # USER AUTHENTICATION METHOD ----------
    async def authenticate_user(self, username: str, password: str) -> Token:
        async with self.async_session as session:
            result = await session.execute(select(models.User).filter_by(username=username))
            user = result.scalar()

            # Handle exception if user doesn't exist
            if not user:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            # Fetching for user's hashed password
            result = await session.execute(select(models.User.hashed_password).filter_by(id=user.id))
            hashed_password = result.scalar()
            if not hashed_password:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail="Password is incorrect",
                )

            # Handle exception when couldn't verify password
            if not self.verify_password(password, hashed_password):
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED,
                    detail="Cannot validate credentials"
                )

            return self.create_token(user)

    # GET ALL USERS METHOD ----------
    async def get_users(self):
        async with self.async_session as session:

            # Fetch the database and get all users
            result = await session.execute(select(models.User))
            users = result.scalars().all()

            # Return a list of users according to the model BaseUser
            return [BaseUser.model_validate(user) for user in users]
