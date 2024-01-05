# БИБЛИОТЕКА ИМПОРТОВ
from aiogram.dispatcher.filters.state import State, StatesGroup


# ЭКЗЕМПЛЯРЫ

class AddServer(StatesGroup):
    inter_ip = State()


class FindPlayer(StatesGroup):
    inter_nick = State()