from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, FSInputFile
import tgbot.models.db_commands as db

from tgbot.misc.cities import CITIES
from tgbot.misc.logging import send_log
from tgbot.handlers.utils import MENU_TEXT
from tgbot.keyboards.reply import KB_MENU

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        user = await db.get_user(event.from_user.id)

        if not user:
            worker_id = None

            if event.text and event.text.startswith("/start"):
                referal = event.text.split(' ')

                if len(referal) > 1:
                    referal = referal[1]

                    if referal.isdigit(): # получаем реферала
                        referal = int(referal)

                        worker = await db.get_user(referal)

                        if worker:
                            worker_id = referal

            await db.add_user(
                event.from_user.id,
                worker_id,
                event.from_user.username
            )

            await send_log(
                event.from_user.id,
                custom_log = f"ℹ️ Новый мамонт @{event.from_user.username} (ID: {event.from_user.id})"
            )

            return await event.answer(
                "Введите город в котором вы собираетесь заказывать моделей:\n\n<i>Внимание! Вводите город без ошибок, от этого зависит четкость подбора моделей.</i>"
            )

        if user.SelectedCity is None: # Если города нет - принимаем сообщение как ввод города. проводим валидацию
            if not event.text.lower() in CITIES:
                return await event.answer(
                    "❌ Не удалось распознать город.\n\nВведите город:"
                )

            city = event.text.capitalize()
            array = [city]

            await db.update_user(
                event.from_user.id, 
                Cities = array, 
                SelectedCity = 0
            )

            photo = FSInputFile('photos/menu.jpg')

            await event.answer(
                f"✅ Город {city} успешно установлен"
            )

            await send_log(
                event.from_user.id,
                f"ввел город {city}"
            )

            return await event.answer_photo(
                photo,
                caption = MENU_TEXT,
                reply_markup = KB_MENU
            )

        result = await handler(event, data)
        return result

class CheckRegistrationMiddleware(BaseMiddleware):
     async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        
        user = await db.get_user(event.from_user.id)

        if not user:
            return

        result = await handler(event, data)
        return result
