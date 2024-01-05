# БИБЛИОТЕКА ИМПОРТОВ
import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



# КЛАСС ПРОВЕРКИ ПОЛЬЗОВАТЕЛЯ

class CheckUser:
    '''Класс проверки пользователя'''

    async def reg(userid: int) -> bool:
        '''Проверка на регистрацию'''

        db = sqlite3.connect('database.db')
        about_user = db.cursor().execute(f'SELECT full_name FROM users WHERE id = {userid}').fetchone()
        db.close()
        
        if about_user:
            return True
        else:
            return False
        
    
    async def added_servers(userid: int) -> InlineKeyboardMarkup:
        '''Возвращает клавиатуру из добавленных серверов'''

        keyboard = InlineKeyboardMarkup(row_width=2)

        db = sqlite3.connect('database.db')
        my_servers = db.cursor().execute(f'SELECT server_title, local_number FROM added_servers WHERE id = {userid}').fetchall()
        for title, number in my_servers:
            keyboard.insert(button=InlineKeyboardButton(text=title, callback_data=f'server:{number}'))
        db.close()

        keyboard.row(InlineKeyboardButton(text='Создать', callback_data='server:add'))
        keyboard.row(InlineKeyboardButton(text='Закрыть', callback_data='server:close'))

        return keyboard


# КЛАСС ДЕЙСТВИЙ С ПОЛЬЗОВАТЕЛЕМ

class ActionUser:
    '''Класс действий с пользователем'''

    async def new_user(user: list[int, str]) -> None:
        '''Добавляет нового пользователя в базу данных'''

        db = sqlite3.connect('database.db')
        db.cursor().execute(f'INSERT INTO users (id, full_name) VALUES (?,?)',
                            (user[0], user[1]))
        db.commit()
        db.close()


    async def chose_server_for_find(userid: int) -> InlineKeyboardMarkup:
        '''Возвращает клавиатуру из серверов для выбора'''

        keyboard = InlineKeyboardMarkup(row_width=2)

        db = sqlite3.connect('database.db')
        my_servers = db.cursor().execute(f'SELECT server_title, local_number FROM added_servers WHERE id = {userid}').fetchall()
        for title, number in my_servers:
            keyboard.insert(button=InlineKeyboardButton(text=title, callback_data=f'chose_server:{number}'))
        db.close()

        keyboard.row(InlineKeyboardButton(text='Закрыть', callback_data='server:close'))

        return keyboard