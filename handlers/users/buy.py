from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext

import tgbot.models.db_commands as db
import tgbot.keyboards.inline as kb_inline
import tgbot.handlers.utils as msg_utils

from tgbot.misc.states import BookState, AdditionalServicesState, CheckPayState
from tgbot.misc.logging import send_log

user_buy_router = Router()

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 4))
async def buy(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
	product_id = callback_data.product_id

	await callback.message.delete()

	return await callback.message.answer(
		msg_utils.COFIRM_BUY_TEXT,
		reply_markup = kb_inline.confirm_buy_markup(product_id)
	)

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 6))
async def confirm_buy(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
	product_id = callback_data.product_id

	await callback.message.delete()

	product = await db.get_product(product_id)

	photo = URLInputFile(product.Photos[0])
	kb = kb_inline.select_buy_period_markup(product)

	return await callback.message.answer_photo(
		photo,
		caption = "Выберите время на которое вы хотите оформить модель:",
		reply_markup = kb
	)

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 7))
async def select_period(callback: CallbackQuery, callback_data: kb_inline.ProductCD, state: FSMContext):
	cost = callback_data.payload
	product_id = callback_data.product_id

	methods = await db.get_methods()
	product = await db.get_product(product_id)

	if cost == product.Cost:
		tariff = 1
	elif cost == product.CostPerTwoHours:
		tariff = 2
	else:
		tariff = 3

	if not product.AdditionalServices:
		kb = kb_inline.select_pay_method_markup(methods, cost, product_id)

		await send_log(
			callback.from_user.id,
			f"нажал оформить модель {product.Name}, {product.Years} лет"
		)

		if await state.get_state() != CheckPayState.Input:
			await state.set_state(CheckPayState.Input)

		await state.update_data(
			product_id = product_id,
			cost = cost,
			tariff = tariff
		)

		return await callback.message.edit_caption(
			caption = "Выберите способ оплаты:",
			reply_markup = kb
		)

	if await state.get_state() == CheckPayState.Input:
		book_info = await state.get_data()
		book_info = book_info['book_info']
	else:
		book_info = None

	await state.set_state(AdditionalServicesState.Input)
	await state.update_data(
		cost = cost, 
		product_id = product_id, 
		selected = [],
		tariff = tariff,
		book_info = book_info
	)

	kb = kb_inline.kb_additionals(product.AdditionalServices, [], product_id)

	return await callback.message.edit_caption(
		caption = "Выберите необходимые дополнительные услуги, если они не нужны, то нажмите \"Далее\"",
		reply_markup = kb
	)

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 8), AdditionalServicesState.Input)
async def select_additional(callback: CallbackQuery, callback_data: kb_inline.ProductCD, state: FSMContext):
	data = await state.get_data()

	product_id = data['product_id']
	selected = data['selected']
	id = callback_data.payload

	product = await db.get_product(product_id)

	if id in selected:
		selected.remove(id)
	else:
		selected.append(id)

	await state.update_data(
		selected = selected
	)

	kb = kb_inline.kb_additionals(product.AdditionalServices, selected, product_id)

	return await callback.message.edit_reply_markup(
		reply_markup = kb
	)

@user_buy_router.callback_query(F.data == "finish_additional", AdditionalServicesState.Input)
async def finish_additional(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()

	product_id = data['product_id']
	selected = data['selected']
	cost = data['cost']
	tariff = data['tariff']
	book_info = data.get('book_info')

	await state.clear()

	product = await db.get_product(product_id)
	methods = await db.get_methods()

	for i, additional in enumerate(product.AdditionalServices):
		if i in selected:
			cost += additional['cost']


	kb = kb_inline.select_pay_method_markup(methods, cost, product_id)

	await send_log(
		callback.from_user.id,
		f"нажал оформить модель {product.Name}, {product.Years} лет"
	)

	await state.set_state(CheckPayState.Input)
	await state.update_data(
		product_id = product_id,
		cost = cost,
		tariff = tariff,
		additionals = selected,
		book_info = book_info
	)

	return await callback.message.edit_caption(
		caption = "Выберите способ оплаты:",
		reply_markup = kb
	)

@user_buy_router.callback_query(kb_inline.PaymentCD.filter(), CheckPayState.Input)
async def select_method_with_state(callback: CallbackQuery, callback_data: kb_inline.PaymentCD, state: FSMContext):
	method_id = callback_data.method
	amount = callback_data.amount
	product_id = callback_data.payload

	data = await state.get_data()

	method = await db.get_method(method_id)

	text = msg_utils.get_pay_text(method, amount)
	kb = kb_inline.i_paid_markup(product_id)

	await state.update_data(
		method_id = method_id
	)

	return await callback.message.edit_caption(
		caption = text,
		reply_markup = kb
	)

@user_buy_router.callback_query(F.data == "i_paid", CheckPayState.Input)
async def i_paid(callback: CallbackQuery, state: FSMContext):
	active_orders = await db.get_user_active_orders(callback.from_user.id)

	if active_orders and len(active_orders) > 2:
		return await callback.answer("❌ Нельзя создать более 3-х заявок на проверку. Ожидайте проверки предыдущих заявок.")

	data = await state.get_data()

	order_id = await db.add_order(
		callback.from_user.id,
		data['product_id'],
		data.get('additionals', []),
		data['tariff'],
		data.get('book_info')
	)

	method = await db.get_method(data['method_id'])
	product = await db.get_product(data['product_id'])
	
	text = msg_utils.get_order_log_text(
		data, 
		method.Name,
		callback.from_user.username,
		callback.from_user.id,
		product
	)

	await send_log(
		callback.from_user.id,
		custom_log = text,
		reply_markup = kb_inline.check_order_markup(order_id)
	)

	return await callback.message.edit_caption(
		caption = "⏳ Заявка принята в обработку. Ожидайте",
		reply_markup = kb_inline.back_to_product_markup(data['product_id'])
	)

@user_buy_router.callback_query(kb_inline.PaymentCD.filter())
async def select_method(callback: CallbackQuery, callback_data: kb_inline.PaymentCD):
	method_id = callback_data.method
	amount = callback_data.amount
	product_id = callback_data.payload

	method = await db.get_method(method_id)

	text = msg_utils.get_pay_text(method, amount)
	kb = kb_inline.payment_markup(product_id)

	return await callback.message.edit_caption(
		caption = text,
		reply_markup = kb
	)

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 5))
async def book_product(callback: CallbackQuery, callback_data: kb_inline.ProductCD, state: FSMContext):
	product_id = callback_data.product_id

	await state.set_state(BookState.Input)
	await state.update_data(product_id = product_id)

	await callback.message.delete()

	return await callback.message.answer(
		msg_utils.BOOK_TEXT
	)

@user_buy_router.message(BookState.Input)
async def book_input(message: Message, state: FSMContext):

	if len(message.text) > 1024:
		return await message.answer("Не более 1024 символов.")

	data = await state.get_data()
	product_id = data['product_id']

	await state.clear()

	await message.answer("✅ Детали бронирования записаны")

	product = await db.get_product(product_id)

	photo = URLInputFile(product.Photos[0])
	kb = kb_inline.select_buy_period_markup(product)

	text = message.text.replace('<', '"').replace('>', '"') # На всякий случай

	await send_log(
		message.from_user.id,
		f"нажал забронировать модель {product.Name}, {product.Years} лет\n\nДетали бронирования:\n{text}"
	)

	await state.set_state(CheckPayState.Input)
	await state.update_data(
		book_info = text
	)

	return await message.answer_photo(
		photo,
		caption = "Выберите время на которое вы хотите оформить модель:",
		reply_markup = kb
	)

@user_buy_router.callback_query(kb_inline.ProductCD.filter(F.action == 3))
async def buy_channel(callback: CallbackQuery, callback_data: kb_inline.ProductCD):
	product_id = callback_data.product_id

	product = await db.get_product(product_id)
	methods = await db.get_methods()

	kb = kb_inline.select_pay_method_markup(methods, product.ChannelCost, product_id)

	await send_log(
		callback.from_user.id,
		f"нажал приватный канал модели {product.Name}, {product.Years} лет"
	)

	return await callback.message.edit_caption(
		caption = "Выберите способ оплаты:",
		reply_markup = kb
	)

@user_buy_router.callback_query(F.data == "check_pay")
async def check_pay(callback: CallbackQuery):
	return await callback.answer(
		"❌ Платёж не найден. Обратитесь в поддержку по кнопке ниже, если оплатили."
	)