from threading import Thread
import time
import db
import WildBerries
import telebot
import datetime
import random
import telebot
import asyncio
import requests

import Config

bot = telebot.TeleBot(Config.TOKEN)
admin_id = 5061120370

def product_monitoring():
	while True:
		print('ok')

		for user in db.get_data():
			try:
				categories = user[8].split(', ')
				category = random.choice(categories)
			except:
				pass

			try:
				if user[2] != 0 and user[9] == '1':
					if user[8] == None or user[8] == '':
						product = random.choice(WildBerries.get_new_products())
						print(product)
						photo = get_card_adult(product)
						bot.send_media_group(user[0], photo)

					else:
						category = random.choice(categories)

						product = random.choice(WildBerries.search(category))['id']
						print(category, product)

						photo = get_card_adult(product)
						bot.send_media_group(user[0], photo)

						del categories[categories.index(category)]
						db.update_data(data={'white_category': ', '.join(categories)}, id=user[0])
						
			except:
				del categories[categories.index(category)]
				db.update_data(data={'white_category': ', '.join(categories)}, id=user[0])

			finally:
				pass


			try:
				articul = user[5].split(' - ')[0]
				product = user[5].split(' - ')[2]
				result = WildBerries.get_card(articul, provider='card')
				
				current_price = result['price']
				base_price = user[5].split(' - ')[1]

				print('Сейчас:', current_price, 'Была:', base_price)

				if int(current_price) < int(base_price):
					bot.send_message(user[0], f'{product} \nЦена снизилась! Теперь она составляет {current_price}руб. (вместо {base_price}руб.) \n\nСсылка: {result["url"]} \n\nОтслеживание этого товара прекращено')
					db.update_data(id=user[0], data={'url_0':'n - n - не задано'})

			except:
				pass

			try:
				articul = user[6].split(' - ')[0]
				product = user[6].split(' - ')[2]
				result = WildBerries.get_card(articul, provider='card')
				
				current_price = result['price']
				base_price = user[6].split(' - ')[1]

				print('Сейчас:', current_price, 'Была:', base_price)

				if int(current_price) < int(base_price):
					bot.send_message(user[0], f'{product} \nЦена снизилась! Теперь она составляет {current_price}руб. (вместо {base_price}руб.) \n\nСсылка: {result["url"]} \n\nОтслеживание этого товара прекращено')
					db.update_data(id=user[0], data={'url_1':'n - n - не задано'})
			except:
				pass			

			try:
				articul = user[7].split(' - ')[0]
				product = user[7].split(' - ')[2]
				result = WildBerries.get_card(articul, provider='card')
				
				current_price = result['price']
				base_price = user[7].split(' - ')[1]

				print('Сейчас:', current_price, 'Была:', base_price)

				if int(current_price) < int(base_price):
					bot.send_message(user[0], f'{product} \nЦена снизилась! Теперь она составляет {current_price}руб. (вместо {base_price}руб.) \n\nСсылка: {result["url"]} \n\nОтслеживание этого товара прекращено')
					db.update_data(id=user[0], data={'url_2':'n - n - не задано'})
			except:
				pass

		time.sleep(10800)


def premium_сountdown():
	day = datetime.datetime.now().day

	while True:
		current_day = datetime.datetime.now().day

		if day != current_day:
			for user in db.get_data():

				if user[2] != 0:
					db.update_data(data={'premium': user[2] - 1}, id=user[0])
					print(user[0], user[2])

					if user[2] == 2:
						bot.send_message(user[0], 'До окончания премиума остался 1 день')

					elif user[2] == 1:
						bot.send_message(user[0], 'Премиум подписка закончилась, вы можете приобрести ее снова /donate')

			day = current_day
			db.update_data(data={'limits': 5})

		time.sleep(1800)
		

def get_card_adult(product_id):
	basket, card_vol, card_part, photo_1, photo_2  = WildBerries.get_basket(product_id)

	result_dict = requests.get(f'https://card.wb.ru/cards/detail?spp=28&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,18,21&sppFixGeo=4&dest=-1075831,-115134,-956089,-1017011&nm={product_id}').json()
	result_dict_basket = requests.get(f'https://basket-{basket}.wb.ru/vol{card_vol}/part{card_part}/{product_id}/info/ru/card.json').json()

	name = result_dict['data']['products'][0]['name']
	price = result_dict['data']['products'][0]['salePriceU'] // 100
	brand = result_dict['data']['products'][0]['brand']
	rating = result_dict['data']['products'][0]['rating']
	feedbacks = result_dict['data']['products'][0]['feedbacks']
	url = f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx'

	try:
		description = result_dict_basket['description']
		if len(description) > 350:
			description = description[:347] + '...'
	except:
		description = 'У товара нет описания🤷‍♂️'

	options = '\n'.join([i['name'] + ' - ' + i['value'] for i in result_dict_basket['options']])
	pics = result_dict['data']['products'][0]['pics']

	photo_url = f'https://basket-{basket}.wb.ru/vol{photo_1}/part{photo_2}/{product_id}/images/big/'

	text = f'*{name} - {brand}* \
			\n*Цена:* {price}руб. \
			\n*Рейтинг:* {rating}🌟 - {feedbacks} отзывов \
			\n\n*Описание: {description}* \
			\n\n*Ссылка:* {url} \
			\n\n*Это если что рекомендация)*'

	photo = []

	# print('картинки', pics)
	if int(basket) == 1:
		if pics < 3:
			# print('менее 3')
			photo.append(telebot.types.InputMediaPhoto(photo_url + '1.webp', text, parse_mode="MARKDOWN"))
		else:
			photo.append(telebot.types.InputMediaPhoto(photo_url + '1.webp', text, parse_mode="MARKDOWN"))
			photo.append(telebot.types.InputMediaPhoto(photo_url + '2.webp', parse_mode="MARKDOWN"))
			photo.append(telebot.types.InputMediaPhoto(photo_url + '3.webp', parse_mode="MARKDOWN"))

	else:
		if pics < 3:
			photo.append(telebot.types.InputMediaPhoto(photo_url + '1.jpg', text, parse_mode="MARKDOWN"))
		else:
			photo.append(telebot.types.InputMediaPhoto(photo_url + '1.jpg', text, parse_mode="MARKDOWN"))
			photo.append(telebot.types.InputMediaPhoto(photo_url + '2.jpg', parse_mode="MARKDOWN"))
			photo.append(telebot.types.InputMediaPhoto(photo_url + '3.jpg', parse_mode="MARKDOWN"))

	return photo


premium_count = Thread(target=premium_сountdown)
premium_count.start()

product_monitoring_thread = Thread(target=product_monitoring)
product_monitoring_thread.start()