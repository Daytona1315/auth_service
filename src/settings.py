from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    server_port: int
    server_host: str
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_url: str
    jwt_secret: str
    jwt_algorithm: str = 'HS256'
    jwt_expiration: int = 3600
    redis_host: str
    redis_port: int
    redis_password: str


settings = Settings(
    _env_file='../.env',
    _env_file_encoding='utf-8',
)
