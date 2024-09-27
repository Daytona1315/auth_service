from tortoise import Tortoise
from src.database.db_config import config


if __name__ == "__main__":
    async def initialize():
        await Tortoise.init(
            config=config,
        )

        await Tortoise.generate_schemas()
