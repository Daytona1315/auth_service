from fastapi import (
    APIRouter,
)


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.get('/hello')
def sample():
    return 'hello'
