'''Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.'''

import requests
import json

response = requests.get('https://api.github.com/users/sokolenkomikhail/repos')

with open('git_repos.json', 'w') as f_obj:
    f_obj.write(response.text)

with open('git_repos.json', 'r') as read_f:
    data = json.load(read_f)
    for i in data:
        print(i['name'])
