from fastapi import FastAPI

from src.routers.auth_router import router as auth_router
from src.routers.utilities_service import router as utils_router

app = FastAPI( 
    title='Auth service'
)

app.include_router(
    router=auth_router,
)

app.include_router(
    router=utils_router,
)


