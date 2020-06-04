'''Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.'''

'''Фотографии Земли из космоса по выбранным координатам. 
Документация к API: 
https://api.nasa.gov/ (раздел Earth в нижней части страницы).
Можно получить фото по интересующим координатам и нужной дате. 
В словаре cities содержатся названия городов и их координаты'''

import requests

key = ''

cities = {'Moscow': {'lat': 55.75222, 'lon': 37.61556},
          'Saint Petersburg': {'lat': 59.9386300, 'lon': 30.3141300},
          'Paris': {'lat': 48.8534, 'lon': 2.3488},
          'New York': {'lat': 40.7143, 'lon': -74.006},
          'Beijing': {'lat': 39.9075000, 'lon': 116.3972300}}

params = {'lat': cities['Moscow']['lat'],
          'lon': cities['Moscow']['lon'],
          'date': '2019-06-14',
          'dim': '0.2',
          'api_key': key}

response = requests.get('https://api.nasa.gov/planetary/earth/imagery?', params=params)

# Сохранение изображения
with open('earth_pic.png', 'wb') as f_obj:
    f_obj.write(response.content)
