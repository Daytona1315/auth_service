from tortoise import Tortoise

from src import settings


db_name: str = settings.db_name
db_host: str = settings.db_host
db_user: str = settings.db_user
db_password: str = settings.db_password


async def initialize():
    await Tortoise.init(
        db_url='',
        modules={'models': ['models']}
    )

    await Tortoise.generate_schemas()
