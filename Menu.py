from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import db

def create_monitoring_menu(premium, user_id):
    url_1 = db.get_data(user_id=user_id)[0][5].split(' - ')[2]
    url_2 = db.get_data(user_id=user_id)[0][6].split(' - ')[2]
    url_3 = db.get_data(user_id=user_id)[0][7].split(' - ')[2]

    if premium:
        if url_1 == 'не задано':
            product_1 = InlineKeyboardButton('Товар 1: задать товар', callback_data='url1_set')
        else:
            product_1 = InlineKeyboardButton('Товар 1: убрать товар', callback_data='url1_remove')

        if url_2 == 'не задано':
            product_2 = InlineKeyboardButton('Товар 2: задать товар', callback_data='url2_set')
        else:
            product_2 = InlineKeyboardButton('Товар 2: убрать товар', callback_data='url2_remove')

        if url_3 == 'не задано':
            product_3 = InlineKeyboardButton('Товар 3: задать товар', callback_data='url3_set')
        else:
            product_3 = InlineKeyboardButton('Товар 3: убрать товар', callback_data='url3_remove')

    else:
        if url_1 == 'не задано':
            product_1 = InlineKeyboardButton('Товар 1: задать товар', callback_data='url1_set')
        else:
            product_1 = InlineKeyboardButton('Товар 1: убрать товар', callback_data='url1_remove')

        product_2 = InlineKeyboardButton('Товар 2: не доступно в бесплатном тарифе', callback_data='NULL')

        product_3 = InlineKeyboardButton('Товар 3: не доступно в бесплатном тарифе', callback_data='NULL')

    return InlineKeyboardMarkup(row_width=1).add(product_1, product_2, product_3)


def create_payments_menu(url, bill_id):
    payments_url = InlineKeyboardButton('Ссылка на оплату', url=url)
    payments_check = InlineKeyboardButton('✔ Проверить оплату', callback_data=f'payments_check:{bill_id}')

    return InlineKeyboardMarkup(row_width=1).add(payments_url, payments_check)


statisics = KeyboardButton('Статистика цен')
monitoring = KeyboardButton('Мониторинг товара')
feedback = KeyboardButton('Написать отзыв')
find_product = KeyboardButton('Найти товар')

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(statisics, monitoring, find_product)
main_menu.add(feedback)


back = KeyboardButton('Главное меню')

back_menu = ReplyKeyboardMarkup(resize_keyboard=True)
back_menu.add(back)


inline_back = InlineKeyboardButton('Назад', callback_data='back')
inline_back_menu = InlineKeyboardMarkup().add(inline_back)


premium_buy = InlineKeyboardButton('Купить Premium⚡️', callback_data='buy_premium')
premium_buy_menu = InlineKeyboardMarkup().add(premium_buy)




