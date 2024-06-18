from tgbot.models.db_commands import add_method

METHODS = ('Банковская карта', 'USDT', 'ETH', 'BTC')
SYMBOLS = ('💳', '💱', '💱', '💱')

CURRENCIES = ('RUB', 'USDT', 'ETH', 'BTC')
RATES = (1, 0.010, 0.0000066, 0.000000396)

IS_CRYPTO = (False, True, True, True)

async def create_default_methods():
	for i in range(len(METHODS)):
		await add_method(METHODS[i], SYMBOLS[i], CURRENCIES[i], RATES[i], IS_CRYPTO[i])

	return True

