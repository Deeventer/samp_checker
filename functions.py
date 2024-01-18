# БИБЛИОТЕКА ИМПОРТОВ
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User
from config import db



# КЛАСС ПРОВЕРКИ ПОЛЬЗОВАТЕЛЯ

class UserService:
    '''Класс действий с пользователем'''

    async def __init__(self, user: User, *args, **kwargs):
        self.user = user


    async def check_register(self) -> bool:
        '''Проверка на регистрацию'''

        return db.cursor().execute(f'SELECT full_name FROM users WHERE id = {self.user.id}').fetchone()
    

    async def add_user(self) -> None:
        '''Регистрирует нового пользователя'''
        db.cursor().execute('INSERT INTO users (id, full_name) VALUES (?,?)',
                            (self.user.id, self.user.full_name))
        db.commit()
        
    
    async def added_servers(self) -> InlineKeyboardMarkup:
        '''Возвращает клавиатуру из добавленных серверов'''

        keyboard = InlineKeyboardMarkup(row_width=2)

        my_servers = db.cursor().execute(f'SELECT server_title, local_number FROM added_servers WHERE id = {self.user.id}').fetchall()
        for title, number in my_servers:
            keyboard.insert(button=InlineKeyboardButton(text=title, callback_data=f'server:{number}'))

        keyboard.row(InlineKeyboardButton(text='Создать', callback_data='server:add'))
        keyboard.row(InlineKeyboardButton(text='Закрыть', callback_data='server:close'))

        return keyboard
    
    
    async def chose_server_for_find(self) -> InlineKeyboardMarkup:
        '''Возвращает клавиатуру из серверов для выбора'''

        keyboard = InlineKeyboardMarkup(row_width=2)
        my_servers = db.cursor().execute(f'SELECT server_title, local_number FROM added_servers WHERE id = {self.user.id}').fetchall()
        for title, number in my_servers:
            keyboard.insert(button=InlineKeyboardButton(text=title, callback_data=f'chose_server:{number}'))

        keyboard.row(InlineKeyboardButton(text='Закрыть', callback_data='server:close'))

        return keyboard