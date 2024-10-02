from fastapi import FastAPI

from src.routers.auth_router import router as auth_router


app = FastAPI( 
    title='Auth service'
)

app.include_router(
    router=auth_router,
)

