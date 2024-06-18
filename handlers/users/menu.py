from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

import tgbot.models.db_commands as db
import tgbot.keyboards.reply as kb_reply
import tgbot.keyboards.inline as kb_inline
import tgbot.handlers.utils as msg_utils

from tgbot.misc.states import AddCityState
from tgbot.misc.cities import CITIES
from tgbot.misc.logging import send_log

user_menu_router = Router()

@user_menu_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await state.clear()

    photo = FSInputFile('photos/menu.jpg')

    return await message.answer_photo(
        photo,
        caption = msg_utils.MENU_TEXT,
        reply_markup = kb_reply.KB_MENU
    )

@user_menu_router.message(F.text.endswith("Профиль") | F.text.endswith("Отмена"))
async def profile(message: Message, state: FSMContext):
    await state.clear()

    user = await db.get_user(message.from_user.id)
    worker = await db.get_worker(user.WorkerID)

    file = FSInputFile('photos/profile.png')
    text = msg_utils.get_profile_text(message.from_user.id, user.Cities[user.SelectedCity], 0, user.Rating, 0)

    if message.text.endswith("Отмена"):
        await message.answer("🔐", reply_markup = kb_reply.KB_MENU)

    return await message.answer_photo(
        file,
        caption = text,
        reply_markup = kb_inline.kb_profile(worker.escort_city_change if worker else True)
    )

@user_menu_router.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    worker = await db.get_worker(user.WorkerID)

    text = msg_utils.get_profile_text(callback.from_user.id, user.Cities[user.SelectedCity], 0, user.Rating, 0)

    return await callback.message.edit_caption(
        caption = text,
        reply_markup = kb_inline.kb_profile(worker.escort_city_change if worker else True)
    )

@user_menu_router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    orders = await db.get_user_confirmed_orders(callback.from_user.id)

    if not orders:
        return await callback.answer(
            "❌ Вы еще не заказывали моделей"
        )

    text = "<b>📋 Список ваших заказов:</b>\n"
    kb = kb_inline.orders_markup(orders)

    for i, order in enumerate(orders):
        product = await db.get_product(order.ProductID)
        
        if not product:
            continue

        if order.Tariff == 1:
            cost = product.Cost
        elif order.Tariff == 2:
            cost = product.CostPerTwoHours
        else:
            cost = product.CostPerNight

        text += f"\n<b>{i + 1}) </b> <code>{product.Name} | {product.Years} лет | {cost}₽</code>"

    await callback.message.delete()
    return await callback.message.answer(
        text, reply_markup = kb
    )

@user_menu_router.callback_query(kb_inline.OrderCD.filter())
async def order_info(callback: CallbackQuery, callback_data: kb_inline.OrderCD):
    order_id = callback_data.order_id
    order = await db.get_order(order_id)

    if not order:
        return

    product = await db.get_product(order.ProductID)

    if not product:
        return

    text = msg_utils.get_order_text(order, product)
    kb = kb_inline.KB_BACK_TO_ORDERS

    await callback.message.delete()
    return await callback.message.answer_photo(
        product.Photos[0],
        caption = text,
        reply_markup = kb
    )

@user_menu_router.callback_query(F.data == "change_city")
async def change_city(callback: CallbackQuery):
    user = await db.get_user(callback.from_user.id)
    worker = await db.get_worker(user.WorkerID)

    if worker and not worker.escort_city_change:
        return

    kb = kb_inline.cities_markup(user.Cities, user.SelectedCity)

    return await callback.message.edit_caption(
        caption = msg_utils.CHANGE_CITY_TEXT,
        reply_markup = kb
    )

@user_menu_router.callback_query(F.data == "add_city")
async def add_city(callback: CallbackQuery, state: FSMContext):
    user = await db.get_user(callback.from_user.id)

    if len(user.Cities) >= 2:
        return await callback.answer("Нельзя добавить более 2-х городов.")

    await state.set_state(AddCityState.Input)
    await callback.message.delete()

    return await callback.message.answer(
        "Введите название города:",
        reply_markup = kb_reply.KB_CANCEL
    )

@user_menu_router.message(AddCityState.Input)
async def input_city(message: Message, state: FSMContext):
    if not message.text.lower() in CITIES:
        return await message.answer(
            "❌ Не удалось распознать город.\n\nВведите город:"
        )

    city = message.text.capitalize()
    user = await db.get_user(message.from_user.id)

    if city in user.Cities:
        return await message.answer(
            "❌ Вы уже добавили этот город.\n\nВведите город:"
        )

    user.Cities.append(city)
    user.SelectedCity = len(user.Cities) - 1

    await state.clear()

    await db.update_user(
        message.from_user.id,
        Cities = user.Cities,
        SelectedCity = user.SelectedCity
    )

    await message.answer(
        f"✅ Город {city} успешно установлен"
    )

    photo = FSInputFile('photos/menu.jpg')

    await send_log(
        message.from_user.id,
        f"добавил новый город - {city}"
    )

    return await message.answer_photo(
        photo,
        caption = msg_utils.MENU_TEXT,
        reply_markup = kb_reply.KB_MENU
    )

@user_menu_router.callback_query(F.data.startswith("change_city:"))
async def select_new_city(callback: CallbackQuery):
    index = int(callback.data.split(':')[1])

    user = await db.get_user(callback.from_user.id)

    if user.SelectedCity == index:
        return await callback.answer(
            "❌ Этот город уже выбран."
        )

    await db.update_user(callback.from_user.id, SelectedCity = index)

    kb = kb_inline.cities_markup(user.Cities, index)

    return await callback.message.edit_reply_markup(
        reply_markup = kb
    )

@user_menu_router.message(F.text.endswith("Информация"))
async def info(message: Message):
    return await message.answer(
        msg_utils.INFO_TEXT,
        reply_markup = kb_inline.KB_INFO
    )

@user_menu_router.message(F.text.endswith("поддержка"))
async def support(message: Message):
    file = FSInputFile("photos/support.png")

    return await message.answer_photo(
        file,
        caption = msg_utils.SUPPORT_TEXT,
        reply_markup = kb_inline.KB_SUPPORT
    )