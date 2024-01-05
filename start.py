# БИБЛИОТЕКА ИМПОРТОВ
import logging

from aiogram.utils.executor import start_polling

from config import dp
import handlers


# ЗАПУСК БОТА

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info(f'Handlers are loaded: {handlers}')

    start_polling(dispatcher=dp,
                  timeout=180,
                  skip_updates=True)