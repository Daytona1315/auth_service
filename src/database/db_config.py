from src.settings import settings


db_host: str = settings.db_host
db_password: str = settings.db_password
db_port: int = settings.db_port
db_user: str = settings.db_user

config: dict = {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "database": "postgres",
                    "host": f"{db_host}",
                    "password": f"{db_password}",
                    "port": f"{db_port}",
                    "user": f"{db_user}",
                    "minsize": 1,
                    "maxsize": 10,
                }
            }
        },
        "apps": {
            "models": {
                "models": ["models"],
                "default_connection": "default",
            }
        },
    }
