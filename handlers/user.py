from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import tgbot.models.db_commands as db

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message):
    await db.add_user(message.from_user.id, "sth")
    user = await db.get_user(message.from_user.id)
    await message.reply(f"Вітаю {user.something}")

    await db.update_something(message.from_user.id, "sth2")
    user = await db.get_user(message.from_user.id)
    await message.reply(f"Вітаю {user.something}")
