from typing import List
from fastapi import APIRouter, Depends

from src.http_exceptions import ServiceUnavailableException
from src.utilities.utilities_service import UtilitiesService
from src.auth.auth_schema import BaseUser


router = APIRouter(
    prefix='/utils',
    tags=['utils'],
)


# GET ALL USERS
@router.get('/users', response_model=List[BaseUser])
async def get_users(service: UtilitiesService = Depends()):
    try:
        users = await service.get_users()
        return users
    except ConnectionRefusedError:
        raise ServiceUnavailableException

