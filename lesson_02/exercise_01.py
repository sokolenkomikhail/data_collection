'''1) Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайта
superjob.ru и hh.ru. Приложение должно анализировать несколько страниц сайта(также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:

    *Наименование вакансии
    *Предлагаемую зарплату (отдельно мин. и отдельно макс.)
    *Ссылку на саму вакансию
    *Сайт откуда собрана вакансия

По своему желанию можно добавить еще работодателя и расположение. Данная структура должна быть одинаковая для вакансий
с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.

!!!В первую очередь делаем сайт hh.ru - его обязательно. sj.ru можно попробовать сделать вторым. Он находится в очень
странном состоянии и возможна некорректная работа.!!!
'''

import requests
from bs4 import BeautifulSoup
import pandas as pd


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


def headhunter(text):
    main_link = 'https://hh.ru'

    df = pd.DataFrame(columns=['position', 'company', 'location', 'min_salary', 'max_salary', 'currency', 'link'])

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}

    page = 0
    next_page = 0
    while next_page is not None:
        params = {'text': text,
                  'page': page}

        response = requests.get(main_link + '/search/vacancy', headers=headers, params=params)

        soup = BeautifulSoup(response.text, 'lxml')
        main_block = soup.find('div', {
            'class': 'bloko-column bloko-column_l-13 bloko-column_m-9 bloko-column_s-8 bloko-column_xs-4'
        })

        next_page = main_block.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})

        vacancy_block = main_block.find('div', {'class': 'vacancy-serp'})
        vacancies = vacancy_block.findAll('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancies:
            position = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'}).text
            # company = vacancy.find('a', {'class': 'bloko-link bloko-link_secondary'}).text
            company = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info'}).text
            location = vacancy.find('span', {
                'class': 'vacancy-serp-item__meta-info',
                'data-qa': 'vacancy-serp__vacancy-address'
            }).text.replace(' ', ',').split(',')[0].splitlines()[0]
            salary_tag = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            if salary_tag is not None:
                min_salary, max_salary, currency = salaries(salary_tag.text)
            else:
                min_salary, max_salary, currency = None, None, None

            vacancy_link = vacancy.find('a', {'class': 'bloko-link HH-LinkModifier'})['href']
            df = df.append({'position': position,
                            'company': company,
                            'location': location,
                            'min_salary': min_salary,
                            'max_salary': max_salary,
                            'currency': currency,
                            'link': vacancy_link}, ignore_index=True)
        page += 1
    return df


parsing = headhunter('Python')

parsing.to_csv('vacancies.csv')
