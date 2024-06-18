from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

import tgbot.models.db_commands as db
import tgbot.keyboards.inline as kb_inline
import tgbot.handlers.utils as msg_utils

from tgbot.misc.states import AddCityState
from tgbot.misc.cities import CITIES

user_catalog_router = Router()

@user_catalog_router.message(F.text.endswith("Модели"))
async def catalog(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    is_worker = await db.get_worker(message.from_user.id)

    if is_worker:
        worker_id = message.from_user.id
    else:
        worker_id = user.WorkerID

    products = []

    worker = await db.get_worker(worker_id)
    default_products = await db.get_default_productions(user.SelectedCity)

    if worker:
        if default_products:
            if (user.SelectedCity == 0 and worker.escort_default_productions_1) or (user.SelectedCity == 1 and worker.escort_default_productions_2):
                products += default_products

        worker_products = await db.get_worker_productions(user.SelectedCity, worker_id)
        if worker_products:
            products += worker_products

    else:
        products = default_products

    kb = kb_inline.productions_markup(products, 0)

    return await message.answer(
        f"🎁 Все анкеты проходили строгую проверку личности нашим агентством.\n\nСейчас свободно: <b>{len(products)} девушек</b>",
        reply_markup = kb
    )

@user_catalog_router.callback_query(kb_inline.ProductsPageCD.filter())
async def catalog_page(callback: CallbackQuery, callback_data: kb_inline.ProductsPageCD):
    page = callback_data.page
    delete_msg = callback_data.delete_msg

    user = await db.get_user(callback.from_user.id)
    is_worker = await db.get_worker(callback.from_user.id)

    if is_worker:
        worker_id = callback.from_user.id
    else:
        worker_id = user.WorkerID

    products = []

    worker = await db.get_worker(worker_id)
    default_products = await db.get_default_productions(user.SelectedCity)

    if worker:
        if default_products:
            if (user.SelectedCity == 0 and worker.escort_default_productions_1) or (user.SelectedCity == 1 and worker.escort_default_productions_2):
                products += default_products

        worker_products = await db.get_worker_productions(user.SelectedCity, worker_id)
        if worker_products:
            products += worker_products

    else:
        products = default_products

    kb = kb_inline.productions_markup(products, page)
    text = f"🎁 Все анкеты проходили строгую проверку личности нашим агентством.\n\nСейчас свободно: <b>{len(products)} девушек</b>"

    if not delete_msg:
        return await callback.message.edit_text(
            text,
            reply_markup = kb
        )

    await callback.message.delete()

    return await callback.message.answer(
        text,
        reply_markup = kb
    )

@user_catalog_router.callback_query(kb_inline.ProductCD.filter(F.action == 0))
async def product_info(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
    product_id = callback_data.product_id
    page = callback_data.page

    product = await db.get_product(product_id)
    user = await db.get_user(callback.from_user.id)

    if not product:
        return

    text = msg_utils.get_product_text(
        product.Name,
        user.Cities[user.SelectedCity],
        product.Years,
        product.Cost,
        product.CostPerTwoHours,
        product.CostPerNight,
        product.Description,
        product.Services
    )

    kb = kb_inline.product_markup(product, page)
    photo = URLInputFile(product.Photos[0])

    await callback.message.delete()

    return await callback.message.answer_photo(
        photo,
        caption = text,
        reply_markup = kb
    )

@user_catalog_router.callback_query(kb_inline.ProductCD.filter(F.action == 1))
async def additional_services(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
    product_id = callback_data.product_id
    product = await db.get_product(product_id)

    text = "😍 Дополнительные услуги модели:\n\n"
    kb = kb_inline.back_to_product_markup(product_id)

    for service in product.AdditionalServices:
        text += f"<b>{service['name']}</b> - {service['cost']}₽\n"

    return await callback.message.edit_caption(
        caption = text,
        reply_markup = kb
    )

@user_catalog_router.callback_query(kb_inline.ProductCD.filter(F.action == 2))
async def product_change_photo(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
    product_id = callback_data.product_id
    current_photo = callback_data.payload
    page = callback_data.page

    product = await db.get_product(product_id)

    if len(product.Photos) < 2:
        return await callback.answer("Больше фотографий нет.")

    user = await db.get_user(callback.from_user.id)

    if not product:
        return

    photo_index = current_photo + 1 if (current_photo + 1) < len(product.Photos) else 0
    
    text = msg_utils.get_product_text(
        product.Name,
        user.Cities[user.SelectedCity],
        product.Years,
        product.Cost,
        product.CostPerTwoHours,
        product.CostPerNight,
        product.Description,
        product.Services
    )

    photo = URLInputFile(product.Photos[photo_index])
    kb = kb_inline.product_markup(product, page, photo_index)

    return await callback.message.edit_media(
        media = InputMediaPhoto(media = photo, caption = text),
        reply_markup = kb
    )