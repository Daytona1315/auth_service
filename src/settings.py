from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_port: int
    server_host: str
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)
