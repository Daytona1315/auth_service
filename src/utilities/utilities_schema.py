from pydantic import BaseModel


class CredentialsTable(BaseModel):
    id: int
    user_id: int
    username: str
    hashed_password: str


class UserTable(BaseModel):
    username: str
    email: str
