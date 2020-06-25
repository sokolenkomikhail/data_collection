''' Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные
вакансии в созданную БД'''

'''Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы'''

'''Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта'''

import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
from pprint import pprint


# Приведение зарплат из строкового типа в числовой
def salaries(string):
    sal_min, sal_max = None, None
    for idx, s in enumerate(string[3:]):
        if s.isalpha():
            break
    curr = string[idx+3:]
    if string[:2] == 'до':
        sal_max = int(''.join([n for n in string[3:] if n.isdigit()]))
    elif string[:2] == 'от':
        sal_min = int(''.join([n for n in string[3:] if n.isdigit()]))
    else:
        min_max_salary = string.split('-')
        sal_min = int(''.join([n for n in min_max_salary[0] if n.isdigit()]))
        sal_max = int(''.join([n for n in min_max_salary[1] if n.isdigit()]))
    return sal_min, sal_max, curr


def to_dict(data):
    '''Функция на вход получает блок вакансии. Возвращает словарь с приведенными данными'''
    position = data.find('a', {'class': 'bloko-link HH-LinkModifier'}).text
    company = data.find('div', {'class': 'vacancy-serp-item__meta-info'}).text.replace(u'\xa0', '')
    location = data.find('span', {
        'class': 'vacancy-serp-item__meta-info',
        'data-qa': 'vacancy-serp__vacancy-address'
    }).text.replace(' ', ',').split(',')[0].splitlines()[0]
    salary = data.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary is not None:
        min_salary, max_salary, currency = salaries(salary.text)
    else:
        min_salary, max_salary, currency = None, None, None
    vacancy_link = data.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
    vacancy_id = int(vacancy_link[22:30])
    dict = {'vacancy_id': vacancy_id,
            'position': position,
            'company': company,
            'location': location,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'currency': currency,
            'link': vacancy_link}
    return dict


def get_vacancies(text):
    '''функция на вход получает текстовый запрос для поиска на hh.ru. В цикле склееивает результаты работы метода
    'findAll' со всех доступных страниц в один список и затем возвращает его'''
    page = 0
    next_page = 0
    all_vacancies = []
    while next_page is not None:
        main_link = 'https://hh.ru'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        params = {'text': text,
                  'page': page}

        response = requests.get(main_link + '/search/vacancy', headers=headers, params=params)

        soup = BeautifulSoup(response.text, 'lxml')
        # основной блок
        main_block = soup.find('div', {
            'class': 'bloko-column bloko-column_l-13 bloko-column_m-9 bloko-column_s-8 bloko-column_xs-4'
        })
        # блок с вакансиями
        vacancy_block = main_block.find('div', {'class': 'vacancy-serp'})
        # поиск вакансий в блоке
        page_vacancies = vacancy_block.findAll('div', {'class': 'vacancy-serp-item'})
        # объединение в один список
        all_vacancies += page_vacancies
        # поиск кнопки перехода на следующую страницу
        next_page = main_block.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        page += 1
    return all_vacancies


# Вставка вакансий в БД
# Для каждого нового запроса по ключевому слову создается новая коллекция с таким же названием
def insert_into_db(text, host):
    client = MongoClient(host, 27017)
    db = client['vacancies_db']
    vacancies = db[text]
    for i in get_vacancies(text):
        vacancies.insert_one(to_dict(i))
    return vacancies


# insert_into_db('Data scientist', '192.168.1.67')


# Поиск вакансий с зарплатой выше, либо равной переданной в функцию
def high_salaries(collection, value):
    client = MongoClient('192.168.1.67', 27017)
    db = client['vacancies_db']
    vacancies = db[collection]
    vac_list = []
    for vacancy in vacancies.find({'$or': [{'min_salary': {'$gte': value}}, {'max_salary': {'$gte': value}}]},
                                  {'_id': 0, 'position': 1, 'link': 1, 'min_salary': 1, 'max_salary': 1}):
        vac_list.append(vacancy)
    return vac_list


pprint(high_salaries('Data scientist', 100000))


# Вставка в БД только новых вакансий
def insert_new(text, host):
    client = MongoClient(host, 27017)
    db = client['vacancies_db']
    vacancies = db[text]
    for i in get_vacancies(text):
        vacancies.update_one({'vacancy_id': to_dict(i)['vacancy_id']}, {'$set': to_dict(i)}, upsert=True)
    return vacancies


insert_new('Data scientist', '192.168.1.67')
