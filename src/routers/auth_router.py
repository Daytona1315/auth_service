from fastapi import APIRouter, Depends

from ..schemas.auth_schema import (
    UserCreate,
    Token, User,
    UserLogin,
)
from src.services.auth_service import AuthService

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


@router.post('/sign-up', response_model=Token)
async def sign_up(user_data: UserCreate,
                  service: AuthService = Depends()
                  ):
    await service.register_new_user(user_data)


@router.post('/sign-in', response_model=Token)
async def sign_in(form_data: UserLogin,
                  service: AuthService = Depends()
                  ):
    await service.authenticate_user(
        form_data.username,
        form_data.password,
    )


@router.get('/user', response_model=User)
async def get_user(user: User = Depends(AuthService.get_current_user)):
    await user
