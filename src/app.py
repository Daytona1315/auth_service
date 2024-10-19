from fastapi import FastAPI

from src.auth.auth_router import router as auth_router
from src.utilities.utilities_router import router as utils_router

app = FastAPI( 
    title='Auth service'
)

app.include_router(
    router=auth_router,
)

app.include_router(
    router=utils_router,
)


