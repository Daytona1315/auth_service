from typing import List
from fastapi import APIRouter, Depends

from src.services.utilities_service import UtilitiesService
from src.schemas.auth_schema import BaseUser


router = APIRouter(
    prefix='/utils',
    tags=['utils'],
)


# GET ALL USERS
@router.get('/users', response_model=List[BaseUser])
async def get_users(service: UtilitiesService = Depends()):
    users = await service.get_users()
    return users
