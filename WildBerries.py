import requests
import codecs
from aiogram.types import InputFile, InputMediaPhoto, ParseMode, MediaGroup
from aiogram.utils.markdown import text, bold, italic, code, pre, link
from aiogram import types
import asyncio
import time
import random



def get_new_products():
	idies = []

	categories = requests.get('https://news.wildberries.ru/tops/site').json()

	for category in categories:
		if category in ['video', 'tovary-dlya-vzroslyh', 'new-video', 'digital-books', 'zdorove', 'tovary-dlya-zhivotnyh', 'detyam', 'dachniy-sezon', 'pitanie', 'dom-i-dacha', 'instrumenty', 'yuvelirnye-ukrasheniya', 'obuv']:
			continue

		for sub_category in categories[category]:
			# print(category, sub_category)
			idies.extend(categories[category][sub_category]['nms'])

	return idies


def selection(query):
	try:
		cards = search(query)
		cheapest = search(query, sort='priceup')
		cards.extend(cheapest)

		register = {}

		prices = [i['salePriceU'] for i in cards]
		prices_average = sum(prices) / len(prices)
		throughput = prices_average / 10

		result = []

		for card in cards:
			# if card['rating'] >= 4 and card['salePriceU'] - prices_average < throughput:
			if card['rating'] >= 4 and card['pics'] > 3 and card['salePriceU'] - prices_average < throughput:
				register[card['id']] = card['feedbacks']
				result.append(card['id'])

				for two_step_filter in cards:
					if two_step_filter['brand'] == card['brand']:
						del cards[cards.index(two_step_filter)]

	except:
		result = ['0000000000000000', '000000000000', '00000000000']

	return result


def create_statistics(query):
	name = '+'.join(query.split())

	prices_popular = search(query)

	if prices_popular == False:
		return 'Не удалось найти товары'

	prices_priceup = search(query, sort='priceup')

	popular_url = f'https://www.wildberries.ru/catalog/{prices_popular[0]["id"]}/detail.aspx'
	cheapest_url = f'https://www.wildberries.ru/catalog/{prices_priceup[0]["id"]}/detail.aspx'

	prices_popular = [i['salePriceU'] for i in prices_popular]
	prices_popular.extend([i['salePriceU'] for i in prices_priceup])


	most_popular_wb = prices_popular[0] // 100
	average_wb = (sum(prices_popular) / len(prices_popular)) // 100
	cheapest_wb = min(prices_popular) // 100

	#формирование ответа для вб
	result_wb = f'{link("Самый дешевый товар", cheapest_url)}: {cheapest_wb}руб \
				\nСредняя цена: {average_wb}руб. \
				\n{link("Самый популярный товар", popular_url)}: {most_popular_wb}руб. '
				# \nСсылка: https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search={name}'

	return result_wb


def search(query, provider='wb', sort='popular', page=1):
	'''собирает цены с интернет магазина

	   query = товар который нужно найти
	   provider = wb, ali
	   sort = пока только для ВБ, popular, priceup, pricedown'''

	#собираем цены с Валйдбериза

	if provider == 'wb':

		#отправка запроса
		url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,18,21&curr=rub&dest=-1075831,-115134,-956089,-1017011&emp=0&lang=ru&locale=ru%page={page}&pricemarginCoeff=1.0&query={query}&reg=1&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31&resultset=catalog&sort={sort}&spp=28&sppFixGeo=4&suppressSpellcheck=false'
		r = requests.get(url)
		prices = r.json()

		# print(prices)

		#если ответ не пустой - возращаем цены
		if bool(prices):
			if bool(prices['data']['products']):
				return prices['data']['products']
			else:
				return False
		else:
			return False

	#собираем цены с АлиЭкспресс
	if provider == 'ali':

		#отправка запроса
		url = f'https://aliexpress.ru/wholesale?SearchText={query}'
		r = requests.get(url)

		#инициализация парсера
		soup = BeautifulSoup(r.text, 'html.parser')

		#собираем цены в список
		prices_ali = soup.find_all('div', {'class':['snow-price_SnowPrice__mainM__18x8np']})
		prices_ali = [int(float((price.text[:-4].replace(',', '.')).replace(' ', '')) * 100) for price in prices_ali]

		#если ответ не пустой - возращаем цены
		if bool(prices_ali):
			return prices_ali
		else:
			return False


def calculating(prices_wb, prices_ali, name):
	name = '+'.join(name.split())

	# формирование статистики для Вайлдбериз
	if prices_wb != False:
		most_popular_wb = prices_wb[0] // 100
		average_wb = (sum(prices_wb) / len(prices_wb)) // 100
		cheapest_wb = min(prices_wb) // 100

		#формирование ответа для вб
		result_wb = f'Самый дешевый товар: {cheapest_wb}руб \
					\nСредняя цена: {average_wb}руб. \
					\nСамый популярный товар: {most_popular_wb}руб. \
					\nСсылка: https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search={name}'
	else:
		result_wb = 'Не удалось найти подходящие товары'

	# формирование статистики для АлиЭкспресс
	if prices_ali != False:
		most_popular_ali = prices_ali[0] // 100
		average_ali = (sum(prices_ali) / len(prices_ali)) // 100
		cheapest_ali = min(prices_ali) // 100

		#формирование ответа для али
		result_ali = f'Самый дешевый товар: {cheapest_ali}руб \
					\nСредняя цена: {average_ali}руб. \
					\nСамый популярный товар: {most_popular_ali}руб. \
					\nСсылка: https://aliexpress.ru/wholesale?SearchText={name}'
	else:
		result_ali = 'Не удалось найти подходящие товары'

	return result_wb, result_ali



def get_card(product_id, provider = 'basket'):
	product_id = str(product_id)

	if provider == 'basket':

		basket, card_vol, card_part, photo_1, photo_2  = get_basket(product_id)

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
				\n\n*Ссылка:* {url}'

		photo = []

		# print('картинки', pics)
		if int(basket) == 1:
			if pics < 3:
				# print('менее 3')
				photo.append(InputMediaPhoto(photo_url + '1.webp', text, parse_mode=types.ParseMode.MARKDOWN))
			else:
				photo.append(InputMediaPhoto(photo_url + '1.webp', text, parse_mode=types.ParseMode.MARKDOWN))
				photo.append(InputMediaPhoto(photo_url + '2.webp', parse_mode=types.ParseMode.MARKDOWN))
				photo.append(InputMediaPhoto(photo_url + '3.webp', parse_mode=types.ParseMode.MARKDOWN))

		else:
			if pics < 3:
				photo.append(InputMediaPhoto(photo_url + '1.jpg', text, parse_mode=types.ParseMode.MARKDOWN))
			else:
				photo.append(InputMediaPhoto(photo_url + '1.jpg', text, parse_mode=types.ParseMode.MARKDOWN))
				photo.append(InputMediaPhoto(photo_url + '2.jpg', parse_mode=types.ParseMode.MARKDOWN))
				photo.append(InputMediaPhoto(photo_url + '3.jpg', parse_mode=types.ParseMode.MARKDOWN))

		return photo

	if provider == 'card':
		result_dict = requests.get(f'https://card.wb.ru/cards/detail?spp=28&regions=80,64,83,4,38,33,70,82,69,68,86,30,40,48,1,22,66,31&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,18,21&sppFixGeo=4&dest=-1075831,-115134,-956089,-1017011&nm={product_id}').json()

		if bool(result_dict['data']['products']):
			name = result_dict['data']['products'][0]['name']
			brand = result_dict['data']['products'][0]['brand']
			price = result_dict['data']['products'][0]['salePriceU'] // 100
			rating = result_dict['data']['products'][0]['rating']
			feedbacks = result_dict['data']['products'][0]['feedbacks']
			url = f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx'

			return {'name': name, 'price': price, 'brand': brand, 'rating': rating, 'feedbacks': feedbacks, 'url': url}

		else:
			return False




def get_id(product_to_find, sort = 'popular'):
	return str(search(product_to_find, sort=sort)['data']['products'][0]['id'])


def get_basket(product_id):
	product_id = str(product_id)

	for basket in range(1, 11):
		if basket == 1:
			pid_vol = product_id[:2]
			pid_part = product_id[:4]


		if 2 <= basket <= 5:
			pid_vol = product_id[:3]
			pid_part = product_id[:5]

			if len(product_id) > 8:
				pid_vol = product_id[:4]
				pid_part = product_id[:6]


		if 6 <= basket <= 7:
			pid_vol = product_id[:4]
			pid_part = product_id[:6]

		if 8 <= basket <= 10:
			pid_vol = product_id[:4]
			pid_part = product_id[:6]

		if basket < 10:
			basket = '0' + str(basket)

		# print(basket)
		r = requests.get(f'https://basket-{basket}.wb.ru/vol{pid_vol}/part{pid_part}/{product_id}/info/ru/card.json')

		if r:
			if int(basket) == 1:
				i_1 = product_id[:2]
				i_2 = product_id[:4]

			if 2 <= int(basket) <= 5:
				i_1 = product_id[:3]
				i_2 = product_id[:5]

				if len(product_id) > 8:
					i_1 = product_id[:4]
					i_2 = product_id[:6]


			if 6 <= int(basket) <= 10:
				i_1 = product_id[:4]
				i_2 = product_id[:6]

			# print(basket)
			return basket, pid_vol, pid_part, i_1, i_2

	else:
		basket = '01'

		pid_vol = product_id[:3]
		pid_part = product_id[:5]

		i_1 = product_id[:3]
		i_2 = product_id[:5]

		r = requests.get(f'https://basket-{basket}.wb.ru/vol{pid_vol}/part{pid_part}/{product_id}/info/ru/card.json')

		if r:
			return basket, pid_vol, pid_part, i_1, i_2


def get_similar_queries(query):
	similar = requests.get(f'https://similar-queries.wildberries.ru/api/v2/search/query?query={query}&spp=34&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=2,12,7,3,6,18,21').json()
	result = []

	for i in similar['query']:
		if query in i:
			result.append(i)

	if bool(result):
		return result
	else:
		return ['нет похожих товаров']


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k

