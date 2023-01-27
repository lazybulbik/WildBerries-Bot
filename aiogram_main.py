from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre, link
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputFile, InputMedia
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio
import random
from fuzzywuzzy import fuzz
from qiwip2py import QiwiP2P
from datetime import timedelta

import Menu
import Config
import WildBerries
import db
import Processing

bot = Bot(Config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

p2p = QiwiP2P(secret_key=Config.QIWI_TOKEN)

admin_id = 5061120370

humiliation = 6


class Forms(Helper):
    mode = HelperMode.snake_case

    STATISTICS = ListItem()
    MONITORING_SET_URL1 = ListItem()
    MONITORING_SET_URL2 = ListItem()
    MONITORING_SET_URL3 = ListItem()
    FEEDBACK = ListItem()
    FIND = ListItem()


def check_premium(chat_id):
    if db.get_data(user_id=chat_id)[0][2] == 0:
        return False

    else:
        return True


@dp.message_handler(commands=['limits'], state='*')
async def limits(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if check_premium(message.from_user.id):
        premium_days = db.get_data(user_id=message.from_user.id)[0][2]
        await message.answer(f'У вас осталось {premium_days} дней премиума. \
                             \nЗа день до окончания срока, вам придет уведомление', reply_markup=Menu.main_menu)

    else:
        search_limit = db.get_data(user_id=message.from_user.id)[0][10]
        await message.answer(f'У вас осталось {search_limit} из 5 бесплатных поисков. \
                             \nЛимит обновляется каждый день, чтобы убрать его преобретите premium - /donate',
                             reply_markup=Menu.main_menu)

    await state.reset_state()


@dp.message_handler(commands=['recomendation'], state='*')
async def recomendation(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if check_premium(message.from_user.id):
        if db.get_data(user_id=message.from_user.id)[0][9] == '1':
            db.update_data(data={'recomendation': '0'}, id=message.from_user.id)
            await message.answer('Подбор рекомендаций отключен', reply_markup=Menu.main_menu)

        else:
            db.update_data(data={'recomendation': '1'}, id=message.from_user.id)
            await message.answer('Подбор рекомендаций включен', reply_markup=Menu.main_menu)

    else:
        await message.answer('Приобретите премиум для получения доступа к рекомедациям', reply_markup=Menu.main_menu)

    await state.reset_state()


@dp.message_handler(commands=['donate'])
async def donate(message: types.Message):
    await message.answer_photo(InputFile('media/premium_buy.jpg'), '*Premium* \
                                                        \n\n*Что вы получите при покупке?* \
                                                          \n*1.* Конечно же вы поддерживаете бота, благодаря вам он еще работает :) \
                                                          \n*2.* Вы - приоритетный пользователь, бот будет отвечать быстрее \
                                                          \n*3.* Увеличенный лимит на отслеживание товара с 1 до 3 \
                                                          \n*4.* Рекомендации интересующих вас товаров\
                                                          \n*5.* Неограниченное кол-во поисков \
                                                        \n\n*Стоимость подписки на 30 дней*: 99руб. \n*По истечению срока вам придет уведомление, а деньги сами НЕ спишутся* \
                                                        \n\nНадеемся на вашу поддержку :)',
                               parse_mode=types.ParseMode.MARKDOWN, reply_markup=Menu.premium_buy_menu)


@dp.message_handler(commands=['givepr'])
async def give_premium(message: types.Message):
    if message.from_user.id == admin_id:
        text = message.text.replace('/givepr ', '').split()

        if len(text) == 2:
            if message.from_user.id in [i[0] for i in db.get_data()]:

                db.update_data(id=text[0], data={'premium': text[1]})

                await message.answer(f'Пользователю {text[0]} успешно выдан премиум на {text[1]} дней')
                await bot.send_message(text[0], f'Вам выдали премиум доступ на {text[1]} дней!🥳')

            else:
                await message.answer('Не удалось выдать премиум пользователю')
        else:
            await message.answer('Не удалось выдать премиум пользователю')


@dp.message_handler(commands=['start'], state='*')  # обрабатывает команду /start
async def on_message(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    db.create_user(message)

    await message.answer(
        'Привет! Я - бот для Валдберриз разработанный рамилькой \nВсю информацию можно получить введя /help',
        reply_markup=Menu.main_menu)

    await state.reset_state()  # сбрасывает состояние для текущ. пользователя (шоб не было проблем)


@dp.message_handler(commands=['help'], state='*')
async def help(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await message.answer('*Кратко по возможностям бота* \
                        \n*Статистика цен:* \
                        \nЭта функция позволяет узнать какие цены на товар. \
                        \nПросто введите название товара, все остальное сделает бот) \
                      \n\n*Мониторинг товара:* \
                        \nОтслеживет изменение цены на товар и сообщает при ее понижении \
                        \nС помощью кнопок выберете в какой слот занести товар, вставьте ссылку или артикул. Готово. Как только цена снизится вам придет уведомление\
                      \n\n*Найти товар:* \
                        \nПодбирает товары по запросу \
                        \nВведите название товара, и вам придет 3 подходящих карточки \
                      \n\n*Premium* \
                        \nДает вам преимущества о которых можно почиать в /donate', parse_mode=types.ParseMode.MARKDOWN,
                         reply_markup=Menu.main_menu)

    await state.reset_state()


@dp.message_handler(lambda message: not (message.entities))  # обработка команд главного меню
async def on_message(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if message.text == Menu.statisics.text:  # кнопка статистики
        await message.answer('Введи название товара..', reply_markup=Menu.back_menu)
        await state.set_state(Forms.STATISTICS[0])

    elif message.text == Menu.monitoring.text:  # кнопка мониторинга цен
        premium = check_premium(message.from_user.id)

        url_1 = db.get_data(user_id=message.from_user.id)[0][5].split(' - ')[2]
        url_2 = db.get_data(user_id=message.from_user.id)[0][6].split(' - ')[2]
        url_3 = db.get_data(user_id=message.from_user.id)[0][7].split(' - ')[2]

        monitoring_menu = Menu.create_monitoring_menu(premium, message.from_user.id)

        await message.answer(f'*Ваши отслеживаемые товары:* \
                              \n*Товар 1:* {url_1} \
                              \n*Товар 2:* {url_2} \
                              \n*Товар 3:* {url_3}', parse_mode=types.ParseMode.MARKDOWN, reply_markup=monitoring_menu)


    elif message.text == Menu.feedback.text:  # кнопка отзыва
        await message.answer('Поделитесь мнением о боте', reply_markup=Menu.back_menu)
        await state.set_state(Forms.FEEDBACK[0])

    elif message.text == Menu.find_product.text:  # кнопка поиска товаров
        await message.answer('Введите название товара, который хотите найти..', reply_markup=Menu.back_menu)
        await state.set_state(Forms.FIND[0])


@dp.message_handler(lambda message: not (message.entities), state=Forms.STATISTICS[0])
async def statistics(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    limits = db.get_data(user_id=message.from_user.id)[0][10]

    if message.text == Menu.back.text:  # возращает в главное меню
        await message.answer('Вы в главном меню бота', reply_markup=Menu.main_menu)
        await state.reset_state()
        return

    if check_premium(message.from_user.id) or limits != 0:
        if not check_premium(message.from_user.id):
            await asyncio.sleep(humiliation)

        result = WildBerries.create_statistics(message.text)

        await message.answer(f'*Товары по запросу {message.text}* \n{result}', parse_mode=types.ParseMode.MARKDOWN)

        if check_premium(message.from_user.id):
            if result != 'Не удалось найти товары':
                if db.get_data(user_id=message.from_user.id)[0][8] == None:
                    db.update_data(data={'white_category': message.text}, id=message.from_user.id)

                else:
                    db.update_data(
                        data={'white_category': db.get_data(user_id=message.from_user.id)[0][8] + ', ' + message.text},
                        id=message.from_user.id)

        else:
            db.update_data(data={'limits': limits - 1}, id=message.from_user.id)

    else:
        await message.answer('Ваше кол-во поисков исчерпано. Лимит обновиться завтра', reply_markup=Menu.main_menu)
        await state.reset_state()


@dp.message_handler(lambda message: not (message.entities), state=Forms.FEEDBACK[0])
async def feedback(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if message.text == Menu.back.text:
        await message.answer('Вы в главном меню бота', reply_markup=Menu.main_menu)
        await state.reset_state()
        return

    review = (message.text.lower()).split()

    for word in review:
        for censored_word in Config.censorship:
            if fuzz.ratio(censored_word, word) > 70:
                await message.answer('Моя цензура не позволяет пропустить этот отзыв, переформулируйте')
                return

    await message.answer('Спасибо за обратную связь!', reply_markup=Menu.main_menu)
    await bot.send_message(admin_id, f'*Отзыв от {message.from_user.first_name}:* \n{message.text}',
                           parse_mode=types.ParseMode.MARKDOWN)

    await state.reset_state()


@dp.message_handler(lambda message: not (message.entities), state=Forms.FIND[0])
async def find_product(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    limits = db.get_data(user_id=message.from_user.id)[0][10]

    if message.text == Menu.back.text:  # возращает в главное меню
        await message.answer('Вы в главном меню бота', reply_markup=Menu.main_menu)
        await state.reset_state()
        return

    if check_premium(message.from_user.id) or limits != 0:
        await message.answer('Ищу подходящие варинты.. 🧐')

        if not check_premium(message.from_user.id):
            await asyncio.sleep(humiliation)

        idies = WildBerries.selection(message.text)

        if '0000000000000000' in idies:
            await message.answer_photo(InputFile('media/none.jpg'), 'Не удалось найти товары')
            return

        idq = idies.pop(idies.index(random.choice(idies)))
        print(idq)
        photo_0 = WildBerries.get_card(idq)

        idq = idies.pop(idies.index(random.choice(idies)))
        print(idq)
        photo_1 = WildBerries.get_card(idq)

        idq = idies.pop(idies.index(random.choice(idies)))
        print(idq)
        photo_2 = WildBerries.get_card(idq)

        try:
            await bot.send_media_group(message.from_user.id, photo_0)
        except Exception as e:
            print(e)

        try:
            await bot.send_media_group(message.from_user.id, photo_1)
        except Exception as e:
            print(e)

        try:
            await bot.send_media_group(message.from_user.id, photo_2)
        except Exception as e:
            print(e)

        await message.answer('*Похожие товары: *' + ', '.join(WildBerries.get_similar_queries(message.text)),
                             parse_mode=ParseMode.MARKDOWN)

        if check_premium(message.from_user.id):
            if db.get_data(user_id=message.from_user.id)[0][8] == None:
                db.update_data(data={'white_category': message.text}, id=message.from_user.id)

            else:
                db.update_data(
                    data={'white_category': db.get_data(user_id=message.from_user.id)[0][8] + ', ' + message.text},
                    id=message.from_user.id)

        else:
            db.update_data(data={'limits': limits - 1}, id=message.from_user.id)

    else:
        await message.answer('Ваше кол-во поисков исчерпано. Лимит обновиться завтра', reply_markup=Menu.main_menu)
        await state.reset_state()


@dp.message_handler(lambda message: not (message.entities) or message.entities[0].type == 'url',
                    state=[Forms.MONITORING_SET_URL1[0], Forms.MONITORING_SET_URL2[0], Forms.MONITORING_SET_URL3[0]])
async def monitoring_set_url1(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if await state.get_state() == 'monitoring_set_url1':
        db_key = 'url_0'

    elif await state.get_state() == 'monitoring_set_url2':
        db_key = 'url_1'

    else:
        db_key = 'url_2'

    if 'https' in message.text:
        articul = message.text.split('/')[4]
    else:
        articul = message.text

    card = WildBerries.get_card(articul, provider='card')

    if card != False:
        db.update_data(id=message.from_user.id,
                       data={db_key: str(articul) + ' - ' + str(card['price']) + ' - ' + card['name']})

        premium = check_premium(message.from_user.id)

        url_1 = db.get_data(user_id=message.from_user.id)[0][5].split(' - ')[2]
        url_2 = db.get_data(user_id=message.from_user.id)[0][6].split(' - ')[2]
        url_3 = db.get_data(user_id=message.from_user.id)[0][7].split(' - ')[2]

        monitoring_menu = Menu.create_monitoring_menu(premium, message.from_user.id)

        await message.answer(f'*Ваши отслеживаемые товары:* \
                              \n*Товар 1:* {url_1} \
                              \n*Товар 2:* {url_2} \
                              \n*Товар 3:* {url_3}', parse_mode=types.ParseMode.MARKDOWN, reply_markup=monitoring_menu)

        await state.reset_state()

    else:
        await message.answer('Вы ввели неправильный артикул или ссылку, попробуйте снова')


@dp.callback_query_handler(state='*')
async def process_callback_button(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    premium = check_premium(callback_query.from_user.id)

    if callback_query.data == 'back':
        url_1 = db.get_data(user_id=callback_query.from_user.id)[0][5].split(' - ')[2]
        url_2 = db.get_data(user_id=callback_query.from_user.id)[0][6].split(' - ')[2]
        url_3 = db.get_data(user_id=callback_query.from_user.id)[0][7].split(' - ')[2]

        monitoring_menu = Menu.create_monitoring_menu(premium, callback_query.from_user.id)

        await bot.edit_message_text(f'*Ваши отслеживаемые товары:* \
                              \n*Товар 1:* {url_1} \
                              \n*Товар 2:* {url_2} \
                              \n*Товар 3:* {url_3}', callback_query.from_user.id, callback_query.message.message_id,
                                    parse_mode=types.ParseMode.MARKDOWN, reply_markup=monitoring_menu)

        await state.reset_state()

    if callback_query.data == 'url1_set':
        await bot.edit_message_text('Вставьте ссылку или артикул товара', callback_query.from_user.id,
                                    callback_query.message.message_id, reply_markup=Menu.inline_back_menu)
        await state.set_state(Forms.MONITORING_SET_URL1[0])

    if callback_query.data == 'url2_set':
        await bot.edit_message_text('Вставьте ссылку или артикул товара', callback_query.from_user.id,
                                    callback_query.message.message_id, reply_markup=Menu.inline_back_menu)
        await state.set_state(Forms.MONITORING_SET_URL2[0])

    if callback_query.data == 'url3_set':
        await bot.edit_message_text('Вставьте ссылку или артикул товара', callback_query.from_user.id,
                                    callback_query.message.message_id, reply_markup=Menu.inline_back_menu)
        await state.set_state(Forms.MONITORING_SET_URL3[0])

    if callback_query.data in ['url1_remove', 'url2_remove', 'url3_remove']:

        if callback_query.data == 'url1_remove':
            db_key = 'url_0'

        elif callback_query.data == 'url2_remove':
            db_key = 'url_1'

        else:
            db_key = 'url_2'

        db.update_data(id=callback_query.from_user.id, data={db_key: 'n - n - не задано'})

        url_1 = db.get_data(user_id=callback_query.from_user.id)[0][5].split(' - ')[2]
        url_2 = db.get_data(user_id=callback_query.from_user.id)[0][6].split(' - ')[2]
        url_3 = db.get_data(user_id=callback_query.from_user.id)[0][7].split(' - ')[2]

        monitoring_menu = Menu.create_monitoring_menu(premium, callback_query.from_user.id)

        await bot.edit_message_text(f'*Ваши отслеживаемые товары:* \
                              \n*Товар 1:* {url_1} \
                              \n*Товар 2:* {url_2} \
                              \n*Товар 3:* {url_3}', callback_query.from_user.id, callback_query.message.message_id,
                                    parse_mode=types.ParseMode.MARKDOWN, reply_markup=monitoring_menu)

    if callback_query.data == 'buy_premium':
        if not check_premium(callback_query.from_user.id):
            bill_id = callback_query.message.message_id + random.randint(0, 999999999)

            bill = p2p.create_bill(bill_id=bill_id, amount=99, expiration_datetime=timedelta(minutes=15))

            text = f'*Premium | Оплата* \
                \n\nСумма к оплате: 99руб.\
                  \nВремя дествия квитанции: 15 минут\
                  \n{link("Ссылка на оплату", bill.pay_url)}'

            await bot.send_message(callback_query.from_user.id, text,
                                   reply_markup=Menu.create_payments_menu(bill.pay_url, bill_id),
                                   parse_mode=types.ParseMode.MARKDOWN)

        else:
            await bot.send_message(callback_query.from_user.id, f'У ваc уже имеется премиум подписка')

    if 'payments_check' in callback_query.data:
        check = p2p.get_bill(callback_query.data.split(':')[1])

        if check:
            if check.status_value == 'PAID':

                db.update_data(id=callback_query.from_user.id, data={'premium': 30})
                await bot.send_message(callback_query.from_user.id,
                                       'Вы приобрели премиум на 30 дней. Все ограничения сняты!🥳')
                await bot.send_message(callback_query.from_user.id, 'Теперь бот будет переодически рекомендовать вам товары на основе ваших препдочтений. \
                                                                    \nЕсли вы не хотите получать рассылку введите /recomendation \
                                                                    \nТак же введя /limits можно узнать оставшийся срок подписки')

                await bot.edit_message_text('Оплачено!', callback_query.message.chat.id, callback_query.message.message_id)

            else:
                await bot.send_message(callback_query.from_user.id, 'Вы не оплатили счет!')

        else:
            await bot.send_message(callback_query.from_user.id, 'Не могу найти ваш счет на оплату')


executor.start_polling(dp)
