from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.misc.default_methods import create_default_methods
from tgbot.misc.utils import SUBSCRIPTIONS

import tgbot.models.db_commands as db

import random

admin_router = Router()
admin_router.message.filter(AdminFilter())

# УДАЛИТЬ НА ПРОДЕ

NAMES = ("Милана","София","Полина","Арина","Виктория","Алиса","Алина","Амира","Анна","Варвара","Василиса","Елизавета","Наталья","Вера","Екатерина","Лилия","Валерия","Евгения","Мария","Дарья","Вероника","Анастасия","Ксения","Альбина","Ульяна","Серафима","Мирослава","Ева","Светлана","Ника","Камила","Александра","Таисия","Юлия","Ясмина","Сафия","Кира","Нина","Ольга","Лея","Элина","Мира","Кристина","Майя","Софья","Алия","Ирина","Агата","Лина","Амина")
COSTS = (2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000)

@admin_router.message(Command("add_rnd_model"))
async def add_rnd_model(message: Message):
    name = random.choice(NAMES)
    cost = random.choice(COSTS)
    yers = random.randint(20, 30)

    id = await db.add_product(
        message.from_user.id,
        True,
        1,
        name,
        yers,
        cost,
        "Пиздатая я сука",
        "Да все умею ебать",
        ['https://avatars.mds.yandex.net/i?id=6ce3cb1d9547238ffd421172d82b6b4656eb60c2-8228018-images-thumbs&n=11', 'https://avatars.mds.yandex.net/i?id=16740893fa355755c3a674a8e352e4fc07e5c453-10638416-images-thumbs&n=11', 'https://avatars.mds.yandex.net/i?id=3a695fa3b3a36a6bcf809a99445b3133ec550105-10532251-images-thumbs&n=11']
    )

    return await message.answer(str(id))


@admin_router.message(Command("default_methods"))
async def default_methods(message: Message):

    """
    СОЗДАЕТ ДЕФОЛТНЫЕ МЕТОДЫ ОПЛАТЫ
    """

    await create_default_methods()

    return await message.answer("ok")

@admin_router.message(Command("default_subs"))
async def default_subs(message: Message):

    """
    СОЗДАЕТ ДЕФОЛТНЫЕ ПОДПИСКИ
    """

    for sub in SUBSCRIPTIONS:
        await db.add_sub(sub['name'], sub['desc'], sub['cost'])

    return await message.answer("ok")