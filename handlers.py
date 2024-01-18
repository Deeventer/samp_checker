# БИБЛИОТЕКА ИМПОРТОВ
import aiogram
from samp_client.client import SampClient
from samp_client import exceptions

from config import dp, db
from functions import UserService
from states import *



# /START , РЕГИСТРАЦИЯ

@dp.message_handler(commands='start', state='*')
async def start(msg: aiogram.types.Message):
    user = UserService(user=msg.from_user)
    if await user.check_register():
        await msg.reply('Вы уже зарегистрированы!')
    
    else:
        await user.add_user()
        await msg.answer('Добро пожаловать! Помощь по командам находится в /help .')


# /HELP , ПОДСКАЗКА ПО КОМАНДАМ
        
@dp.message_handler(commands='help', state='*')
async def help(msg: aiogram.types.Message):
    user = UserService(user=msg.from_user)
    if await user.check_register():
        await msg.answer('<b>СПИСОК КОМАНД:</b>\n\n'
                         '- /help : помощь по командам ;\n\n'
                         '- /myservers : взаимодействие с серверами ;\n'
                         '- /find : найти игрока .')
    else:
        await msg.reply('Вы не зарегистрированы! Введите /start .')


# /MYSERVERS , ВЗАИМОДЕЙСТВИЕ С СЕРВЕРАМИ
        
@dp.message_handler(commands=['myservers', 'моисервера'], state='*')
async def my_servers(msg: aiogram.types.Message):
    user = UserService(user=msg.from_user)
    if await user.check_register():
        await msg.reply('Список добавленных серверов:',
                        reply_markup=await user.added_servers())
    
    else:
        await msg.reply('Вы не зарегистрированы! Введите /start .')


@dp.callback_query_handler(aiogram.filters.Text(startswith='server:'), state='*')
async def actions_with_servers(query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    user = UserService(user=query.from_user)
    data = query.data.split(':')
    category = query.data.split(':')[1]

    if await user.check_register():
        await query.answer()

        match category:
            case 'close':
                await query.message.delete()
            
            case 'add':
                await query.message.edit_text('Пожалуйста, введите айпи вашего сервера. Пример ввода: 80.66.71.47:5125',
                                              reply_markup=aiogram.types.InlineKeyboardMarkup(
                                                  inline_keyboard=[
                                                      [aiogram.types.InlineKeyboardButton(text='Отмена', callback_data='server:cancel')]]))
                await AddServer.inter_ip.set()

            case 'cancel':
                await state.reset_state(with_data=True)
                technical = await query.message.edit_text('Действие успешно отменено!')
                await aiogram.asyncio.sleep(15)
                await dp.bot.delete_message(chat_id=technical.chat.id,
                                            message_id=technical.message_id)
                
            case 'back_to_menu':
                await query.message.edit_text('Список добавленных серверов:',
                                              reply_markup=await user.added_servers())

            case 'del':
                db.cursor().execute(f'DELETE FROM added_servers WHERE id = {query.from_user.id} AND local_number = {data[2]}')
                db.commit()

                await query.message.edit_text('Сервер успешно удалён!',
                                              reply_markup=aiogram.types.InlineKeyboardMarkup(
                                                  inline_keyboard=[
                                                      [aiogram.types.InlineKeyboardButton(text='Назад', callback_data='server:back_to_menu')]]))
                
            case 'confirm':
                about_server = await state.get_data()

                local_numbers = db.cursor().execute(f'SELECT local_number FROM added_servers WHERE id = {query.from_user.id}').fetchall()
                my_numbers = [number[0] for number in local_numbers]

                for new_number in range(99999):
                    if new_number in my_numbers:
                        continue
                    else:
                        db.cursor().execute('INSERT INTO added_servers (id, server_ip, server_title, local_number) VALUES (?,?,?,?)',
                                            (query.from_user.id, about_server['ip'], about_server['title'], new_number))
                        db.commit()

                        await query.message.edit_text('Сервер успешно добавлен!',
                                                      reply_markup=aiogram.types.InlineKeyboardMarkup(
                                                          inline_keyboard=[
                                                              [aiogram.types.InlineKeyboardButton(text='Назад', callback_data='server:back_to_menu')]]))
                        break
                db.close()
                await state.reset_state(with_data=True)
                
            case _:

                about_server = db.cursor().execute(f'SELECT server_ip, server_title FROM added_servers WHERE local_number = {category}').fetchone()
                all_server_ip = str(about_server[0]).split(':')

                server_ip = all_server_ip[0]
                server_port = all_server_ip[1]
                server_title = about_server[1]

                try:
                    with SampClient(address=server_ip, port=server_port) as server:
                        info = server.get_server_info()

                        await query.message.edit_text(f'{server_title}({info.players}/{info.max_players})\n\n'
                                                      f'IP: {":".join(all_server_ip)}\n'
                                                      f'- {info.gamemode}({info.language})\n',
                                                      reply_markup=aiogram.types.InlineKeyboardMarkup(
                                                          inline_keyboard=[
                                                              [aiogram.types.InlineKeyboardButton(text='Удалить', callback_data=f'server:del:{category}')],
                                                              [aiogram.types.InlineKeyboardButton(text='Назад', callback_data='server:back_to_menu')]]))
                
                except exceptions as error:
                    await query.message.edit_text(f'Произошла ошибка. Данные от сервера не получены. Ошибка: {error}',
                                                  reply_markup=aiogram.types.InlineKeyboardMarkup(
                                                      inline_keyboard=[
                                                          [aiogram.types.InlineKeyboardButton(text='Назад', callback_data='server:back_to_menu')]]))
    
    else:
        await query.answer('Вы не зарегистрированы! Введите /start .', show_alert=True)


@dp.message_handler(state=AddServer.inter_ip)
async def inter_ip(msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    if ':' in msg.text:
        all_ip = msg.text.split(':')
        ip = all_ip[0]
        port = all_ip[1]

        try:
            with SampClient(address=ip, port=port) as server:
                info = server.get_server_info()

                await msg.answer('Система определила сервер!')
                await msg.answer(f'{info.hostname}({info.language}) [{info.players}/{info.max_players}]')
                await msg.reply('Если сервер определён верно, нажмите на кнопку подтверждения.',
                                reply_markup=aiogram.types.InlineKeyboardMarkup(
                                    inline_keyboard=[
                                        [aiogram.types.InlineKeyboardButton(text='Подтвердить', callback_data='server:confirm'),
                                         aiogram.types.InlineKeyboardButton(text='Отмена', callback_data='server:cancel')]]))
                await state.update_data(ip=f'{server.address}:{server.port}', title=info.hostname)
                
        except exceptions as error:
            await msg.answer(f'Система не смогла определить сервер. Ошибка: {error}')
    
    else:
        await msg.reply('В айпи адресе должен быть знак : !')


# /FIND , ПОИСК В ИГРЕ
        
@dp.message_handler(commands='find', state='*')
async def find_player(msg: aiogram.types.Message):
    user = UserService(user=msg.from_user)
    if await user.check_register():
        await msg.answer('Выберите сервер, на котором хотите найти игрока.',
                         reply_markup=await user.chose_server_for_find())

    else:
        await msg.reply('Вы не зарегистрированы! Введите /start .')


@dp.callback_query_handler(aiogram.filters.Text(startswith='chose_server:'), state='*')
async def inter_nickname(query: aiogram.types.CallbackQuery, state: aiogram.dispatcher.FSMContext):
    user = UserService(user=query.from_user)
    if await user.check_register():
        server = query.data.split(':')[1]

        await FindPlayer.inter_nick.set()
        await state.update_data(server=server)
        await query.message.edit_text('Пожалуйста, введите никнейм или его часть.',
                                      reply_markup=aiogram.types.InlineKeyboardMarkup(
                                          inline_keyboard=[
                                              [aiogram.types.InlineKeyboardButton(text='Отмена', callback_data='server:cancel')]]))
    
    else:
        await query.answer('Вы не зарегистрированы! Введите /start .', show_alert=True)


@dp.message_handler(state=FindPlayer.inter_nick)
async def search_nickname(msg: aiogram.types.Message, state: aiogram.dispatcher.FSMContext):
    part_nickname = msg.text
    data = await state.get_data()

    server = int(data['server'])
    server_ip = db.cursor().execute(f'SELECT server_ip FROM added_servers WHERE id = {msg.from_user.id} AND local_number = {server}').fetchone()
    ip = str(server_ip[0]).split(':')
    
    try:
        with SampClient(address=ip[0], port=ip[1]) as server:
            hostname = server.get_server_info().hostname
            info = server.get_server_clients_detailed()

            players_list = []
            coin_players = []

            for player in info:
                players_list.append(f'- {player[1]}({player[2]} LVL), ping {player[3]} ms\n')

            for player in players_list:
                
                if part_nickname in player:
                    coin_players.append(player)
            
            if len(coin_players) != 0:
                await msg.reply(f'{hostname}. <b>Найдено {len(coin_players)} совпадений!</b>\n\n'
                                f'{"".join(coin_players)}')
            
            else:
                await msg.reply('Игрок с такой частью никнейма не находится на сервере, либо такого аккаунта не существует.')
            
    except exceptions as error:
        await msg.reply(f'При проверке произошла ошибка: {error}')
        
    await state.reset_state(with_data=True)