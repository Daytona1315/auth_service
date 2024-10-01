from typing import List

from fastapi import APIRouter, Depends

from src.schemas.auth_schema import UserCreate, Token, UserLogin, User, BaseUser
from src.services.auth_service import AuthService

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/sign-up', response_model=Token)
async def sign_up(user_data: UserCreate,
                  service: AuthService = Depends()
                  ):
    token = await service.register_new_user(user_data)
    return token


@router.post('/sign-in', response_model=Token)
async def sign_in(form_data: UserLogin,
                  service: AuthService = Depends()
                  ):
    await service.authenticate_user(
        form_data.username,
        form_data.password,
    )


@router.get('/users', response_model=List[BaseUser])
async def get_users(service: AuthService = Depends()):
    users = await service.get_users()
    return users
