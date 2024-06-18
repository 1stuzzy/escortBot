from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import Optional

from tgbot.misc.utils import config

class ProductCD(CallbackData, prefix = 'product'):
	product_id: int
	action: int
	page: Optional[int] = 0
	payload: Optional[int] = None

	"""

	ACTIONS:

	0 - Info
	1 - Additional Services
	2 - Change Photo

	4 - Buy
	6 - Confirm buy
	7 - Select hours

	8 - Select additional service

	"""

class ProductsPageCD(CallbackData, prefix = 'page'):
	page: int
	delete_msg: Optional[bool] = False

class PaymentCD(CallbackData, prefix = 'payment'):
	amount: int
	method: int
	payload: Optional[int] = None

	"""
	
	METHODS:

	0 - Card
	1 - USDT
	2 - ETH
	3 - BTC

	"""

class SubscriptionCD(CallbackData, prefix = 'sub'):
	sub_id: int
	action: int

	"""

	ACTIONS:

	0 - Info
	1 - Buy

	"""

class OrderCD(CallbackData, prefix = 'order'):
	order_id: int

KB_INFO = (
	InlineKeyboardBuilder()

	.button(text = "🛡 Гарантии", url = config.tg_bot.guarantees_link)
	# .button(text = "Отзывы", url = config.tg_bot.reviews_link)

	.adjust(1)
	.as_markup()
)

KB_SUPPORT = (
	InlineKeyboardBuilder()

	.button(text = "Написать", url = f"t.me/{config.tg_bot.support_nick}")

	.as_markup()
)

KB_BACK_TO_ORDERS = (
	InlineKeyboardBuilder()

	.button(text = "⬅️ Назад", callback_data = "my_orders")

	.as_markup()
)

def kb_additionals(additionals: list, selected: list, product_id: int):
	kb = InlineKeyboardBuilder()

	for i, additional in enumerate(additionals):
		kb.button(
			text = f"[{'❌' if i not in selected else '✅'}] - {additional['name']} - {additional['cost']}₽",
			callback_data = ProductCD(product_id = product_id, action = 8, payload = i)
		)

	kb.button(text = "Далее ➡️", callback_data = "finish_additional")
	kb.button(text = "⬅️ Назад", callback_data = ProductCD(product_id = product_id, action = 0))

	kb.adjust(1)

	return kb.as_markup()

def kb_profile(city_change: bool = True):
	kb = InlineKeyboardBuilder()

	kb.button(text = "🗂 Мои заказы", callback_data = "my_orders")

	if city_change:
		kb.button(text = "🌍 Смена города", callback_data = "change_city")

	kb.adjust(1)

	return kb.as_markup()

def subscription_markup(sub_id: int):
	return (
		InlineKeyboardBuilder()

		.button(text = "💘 Купить", callback_data = SubscriptionCD(sub_id = sub_id, action = 1))
		.button(text = "Назад", callback_data = "back_to_subs")

		.adjust(1)
		.as_markup()
	)

def subscriptions_markup(subscriptions: list):
	kb = InlineKeyboardBuilder()

	for sub in subscriptions:
		kb.button(text = sub.Name, callback_data = SubscriptionCD(sub_id = sub.ID, action = 0))

	kb.adjust(1)
	return kb.as_markup()

def back_to_product_markup(product_id: int):
	return (
		InlineKeyboardBuilder()

		.button(text = "⬅️ Назад", callback_data = ProductCD(product_id = product_id, action = 0))

		.as_markup()
	)

def cities_markup(cities: list, selected_city: int):
	kb = InlineKeyboardBuilder()

	for i, city in enumerate(cities):
		kb.button(text = f"{'✅ ' if i == selected_city else ''}{city}", callback_data = f"change_city:{i}")

	kb.button(text = "➕ Добавить город", callback_data = "add_city")
	kb.button(text = "⏪ Назад", callback_data = "profile")

	kb.adjust(1)
	return kb.as_markup()

def productions_markup(products: list, page: int):
	kb = InlineKeyboardBuilder()

	for i, product in enumerate(products[page * 10:(page + 1) * 10]):
		kb.button(
			text = f"(#{i+1 + (page * 10)}) · {product.Name} · {product.Years}",
			callback_data = ProductCD(product_id = product.ID, action = 0, page = page)
		)

	if page >= 1:
		kb.button(text = "⬅️", callback_data = ProductsPageCD(page = page - 1))

	if len(products) > (page + 1) * 10:
		kb.button(text = "➡️", callback_data = ProductsPageCD(page = page + 1))

	kb.adjust(1)

	return kb.as_markup()

def product_markup(product, page: int, current_photo: int = 0):
	kb = InlineKeyboardBuilder()

	if product.AdditionalServices:
		kb.button(text = "Дополнительные услуги", callback_data = ProductCD(product_id = product.ID, action = 1))

	kb.button(text = "Другое фото", callback_data = ProductCD(product_id = product.ID, action = 2, payload = current_photo, page = page))

	if product.ChannelCost:
		kb.button(text = "Приватный канал модели", callback_data = ProductCD(product_id = product.ID, action = 3))

	kb.button(text = "Оформить", callback_data = ProductCD(product_id = product.ID, action = 4))
	kb.button(text = "Забронировать", callback_data = ProductCD(product_id = product.ID, action = 5))

	kb.button(text = "⬅️ Назад", callback_data = ProductsPageCD(page = page, delete_msg = True))

	kb.adjust(1)
	return kb.as_markup()

def confirm_buy_markup(product_id: int):
	return (
		InlineKeyboardBuilder()

		.button(text = "Ознакомлен", callback_data = ProductCD(product_id = product_id, action = 6))

		.as_markup()
	)

def select_buy_period_markup(product):
	return (
		InlineKeyboardBuilder()

		.button(text = f"🌇 Час - {product.Cost}₽",  callback_data = ProductCD(product_id = product.ID, action = 7, payload = product.Cost))
		.button(text = f"🏙 2 Часа - {product.CostPerTwoHours}₽", callback_data = ProductCD(product_id = product.ID, action = 7, payload = product.CostPerTwoHours))
		.button(text = f"🌃 Ночь - {product.CostPerNight}₽",  callback_data = ProductCD(product_id = product.ID, action = 7, payload = product.CostPerNight))

		.button(text = "⬅ Назад", callback_data = ProductCD(product_id = product.ID, action = 0, page = 0))

		.adjust(1)
		.as_markup()
	)

def select_pay_method_markup(methods: list, amount: int, product_id: int = None):
	kb = InlineKeyboardBuilder()

	for method in methods:
		kb.button(text = f"{method.Symbol} {method.Name}", callback_data = PaymentCD(method = method.ID, amount = amount, payload = product_id))

	if product_id:
		kb.button(text = "⬅ Назад", callback_data = ProductCD(product_id = product_id, action = 0, page = 0))

	kb.adjust(1)
	return kb.as_markup()

def payment_markup(product_id: int = None):
	kb = InlineKeyboardBuilder()

	kb.button(text = "🔄 Проверить оплату", callback_data = "check_pay")

	if product_id:
		kb.button(text = "⬅ Назад", callback_data = ProductCD(product_id = product_id, action = 0, page = 0))

	kb.adjust(1)

	return kb.as_markup()

def i_paid_markup(product_id: int = None):
	kb = InlineKeyboardBuilder()

	kb.button(text = "✅ Я оплатил", callback_data = "i_paid")

	if product_id:
		kb.button(text = "⬅ Назад", callback_data = ProductCD(product_id = product_id, action = 0, page = 0))

	kb.adjust(1)

	return kb.as_markup()

def check_order_markup(order_id: int):
	kb = InlineKeyboardBuilder()

	kb.button(text = "✅", callback_data = f"esocrt_order:{order_id}:2")
	kb.button(text = "❌", callback_data = f"esocrt_order:{order_id}:1")

	return kb.as_markup()

def orders_markup(orders: list):
	kb = InlineKeyboardBuilder()

	for i, order in enumerate(orders):
		kb.button(text = str(i + 1), callback_data = OrderCD(order_id = order.ID))

	kb.adjust(5)

	return kb.as_markup()