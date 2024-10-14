from fastapi import APIRouter, Depends

from src.schemas.auth_schema import (
    UserCreate, Token, UserLogin, BaseUser
)
from src.services.auth_service import AuthService

from src.http_exceptions import ServiceUnavailableException


router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)


# NEW USER REGISTRATION
@router.post('/sign-up', response_model=Token)
async def sign_up(user_data: UserCreate,
                  service: AuthService = Depends()
                  ):
    try:
        token = await service.register_new_user(user_data)
        return token
    except ConnectionRefusedError:
        raise ServiceUnavailableException


# USER SIGN IN
@router.post('/sign-in', response_model=Token)
async def sign_in(form_data: UserLogin,
                  service: AuthService = Depends()
                  ):
    try:
        token = await service.authenticate_user(
            form_data.email,
            form_data.password,
        )
        return token
    except ConnectionRefusedError:
        raise ServiceUnavailableException


# GET USER'S DATA
@router.get('/user', response_model=BaseUser)
def get_user(user: BaseUser = Depends(AuthService.get_current_user)):
    """
    Pass a JWT-token in request header.
    Returns user's data: email, username
    """
    try:
        return user
    except ConnectionRefusedError:
        raise ServiceUnavailableException
