from aiogram.fsm.state import StatesGroup, State

class AddCityState(StatesGroup):
	Input = State()

class BookState(StatesGroup):
	Input = State()

class AdditionalServicesState(StatesGroup):
	Input = State()

class CheckPayState(StatesGroup):
	Input = State()