import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.models.database import create_db

from tgbot.handlers.admin import admin_router
from tgbot.handlers.users.menu import user_menu_router
from tgbot.handlers.users.catalog import user_catalog_router
from tgbot.handlers.users.buy import user_buy_router
from tgbot.handlers.users.subscriptions import user_sub_router

from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.registration import RegistrationMiddleware, CheckRegistrationMiddleware

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))

    dp.message.outer_middleware(RegistrationMiddleware())
    dp.callback_query.outer_middleware(CheckRegistrationMiddleware())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    logger.info("Starting bot")
    config = load_config(".env")
    
    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    for router in [
        admin_router,

        user_menu_router,
        user_catalog_router,
        user_buy_router,
        user_sub_router
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)
    await create_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот був вимкнений!")
