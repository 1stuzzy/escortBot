from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile, InputMediaPhoto, FSInputFile
from aiogram.fsm.context import FSMContext

import tgbot.models.db_commands as db
import tgbot.keyboards.inline as kb_inline
import tgbot.handlers.utils as msg_utils

from tgbot.misc.states import BookState

user_sub_router = Router()

@user_sub_router.message(F.text.endswith("Купить подписку"))
async def subs_catalog(message: Message):
	subs = await db.get_all_subs()
	
	kb = kb_inline.subscriptions_markup(subs)
	photo = FSInputFile('photos/menu.jpg')

	return await message.answer_photo(
		photo,
		caption = "<b>✨ Выберите подписку:</b>",
		reply_markup = kb
	)

@user_sub_router.callback_query(F.data == "back_to_subs")
async def back_to_subs(callback: CallbackQuery):
	subs = await db.get_all_subs()
	
	kb = kb_inline.subscriptions_markup(subs)

	return await callback.message.edit_caption(
		caption = "<b>✨ Выберите подписку:</b>",
		reply_markup = kb
	)

@user_sub_router.callback_query(kb_inline.SubscriptionCD.filter(F.action == 0))
async def sub_info(callback: CallbackQuery, callback_data: kb_inline.SubscriptionCD):
	sub_id = callback_data.sub_id
	sub = await db.get_sub(sub_id)

	text = f"<b>{sub.Name}</b>\n\n{sub.Desc}\n\n💵 Цена за месяц: <b>{sub.Cost} RUB</b>"
	kb = kb_inline.subscription_markup(sub_id)

	return await callback.message.edit_caption(
		caption = text,
		reply_markup = kb
	)

@user_sub_router.callback_query(kb_inline.SubscriptionCD.filter(F.action == 1))
async def sub_info(callback: CallbackQuery, callback_data: kb_inline.SubscriptionCD):
	sub_id = callback_data.sub_id
	sub = await db.get_sub(sub_id)

	methods = await db.get_methods()

	kb = kb_inline.select_pay_method_markup(methods, sub.Cost)

	return await callback.message.edit_caption(
		caption = "Выберите способ оплаты:",
		reply_markup = kb
	)