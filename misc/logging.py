from tgbot.misc.utils import main_bot, bot
from tgbot.models.db_commands import get_worker, get_user, update_user

async def get_service_text():
	me = await bot.get_me()

	return f"""🤖 <b>Информация о боте:</b>
├ Сервис: ESCORT
└ Бот: @{me.username}"""

async def send_log(user_id: int, log: str = None, custom_log: str = None, reply_markup = None):
	user = await get_user(user_id)

	if not user:
		return False

	worker = await get_worker(user.WorkerID)

	if not worker:
		await update_user(user.TelegramID, WorkerID = None)
		return False

	if not worker.escort_notification:
		return False

	service_text = await get_service_text()

	if not custom_log:
		text = f"ℹ️ Мамонт @{user.Username} (ID: {user.TelegramID}) {log}\n\n{service_text}"
	else:
		text = custom_log + f"\n\n{service_text}"
	
	try:
		await main_bot.send_message(
			worker.user_id, text, reply_markup = reply_markup
		)
	except Exception as e:
		print(e)
		await update_user(user.TelegramID, WorkerID = None)

	return True