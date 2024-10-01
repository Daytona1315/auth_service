from pydantic import BaseModel


class BaseUser(BaseModel):
    email: str
    username: str


class UserCreate(BaseUser):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseUser):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
