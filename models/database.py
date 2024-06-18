from gino import Gino
from tgbot.misc.utils import config

db = Gino()

async def create_db():
    await db.set_bind(f'postgresql://postgres:{config.db.password}@localhost:5432/{config.db.database}')
    #await db.gino.drop_all()
    await db.gino.create_all()
