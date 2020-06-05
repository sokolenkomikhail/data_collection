'''Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.'''

'''Погода на Марсе за неделю. 
Страница: https://mars.nasa.gov/insight/weather/. 
Документация к API: 
https://api.nasa.gov/, https://api.nasa.gov/assets/insight/InSight%20Weather%20API%20Documentation.pdf
Авторизация по API-Key'''

import requests
import json

key = ''

params = {'api_key': key,
          'feedtype': 'json',
          'ver': '1.0'}

response = requests.get('https://api.nasa.gov/insight_weather/?', params=params)

with open('mars_weather.json', 'w') as f_obj:
    f_obj.write(response.text)

with open('mars_weather.json', 'r') as read_f:
    data = json.load(read_f)
    for sol in data['sol_keys']:
        print(f'Сол {sol} \n'
              f'UTC: {data[sol]["First_UTC"]} - {data[sol]["Last_UTC"]} \n'
              f'Минимальная температура: {data[sol]["AT"]["mn"]}\N{DEGREE SIGN}С \n'
              f'Максимальная температура: {data[sol]["AT"]["mx"]}\N{DEGREE SIGN}С \n'
              f'Минимальное давление: {data[sol]["PRE"]["mn"]} Pa \n'
              f'Максимальное давление: {data[sol]["PRE"]["mx"]} Pa \n')
