from fastapi import FastAPI
from src.routers.auth import router as auth_router

app = FastAPI()

app.include_router(
    router=auth_router,
)
