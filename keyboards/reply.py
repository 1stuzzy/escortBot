from aiogram.utils.keyboard import ReplyKeyboardBuilder

KB_MENU = (
	ReplyKeyboardBuilder()

	.button(text = "💝 Модели")

	.button(text = "✨ Купить подписку")

	.button(text = "👤 Профиль")
	.button(text = "🔎 Информация")

	.button(text = "👩‍💻 Техническая поддержка")

	.adjust(1, 1, 2)
	.as_markup(resize_keyboard = True)
)

KB_CANCEL = (
	ReplyKeyboardBuilder()

	.button(text = "❌ Отмена")

	.as_markup(resize_keyboard = True)
)