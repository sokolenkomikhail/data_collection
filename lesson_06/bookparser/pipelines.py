# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('192.168.1.67', 27017)
        self.db = client.books

    def process_item(self, item, spider):
        if spider.name == 'book24':
            # Авторы
            # Запись в переменную значения из словаря, а затем удаление этой пары ключ-значение из словаря
            book_info = item['authors']

            # Замена переносов, неразрывных пробелов в элементах списка
            for i, val in enumerate(book_info):
                val = val.replace('\n', '').replace('\xa0', '').replace('  ', '')
                book_info[i] = val
            # Перезапись переменной. В новый список не попадают пустые значения из старого
            # Примерный вид списка: ['Автор:', val1, val2, ..., 'Серия:', otherval, ... ..., 'otherkey:', ...]
            book_info = [i for i in book_info if i]

            # Проверка вхождения элемента в список
            authors = None
            if 'Автор:' in book_info:
                authors = []
                # Перебор элементов начинается со следующего элемента
                # Прерывается, если натыкается на ключ (окончание на ':')
                for i in book_info[book_info.index('Автор:') + 1:]:
                    if i[-1] != ':':
                        authors.append(i)
                    else:
                        break
                # При единичной длине, перезаписывается самим элементом
                if len(authors) == 1:
                    authors = authors[0]

            # добавление новой пары в словарь
            item['authors'] = authors

            # Цены
            # Обработка ситуации, когда цены нет
            # Приведение discount_price к int
            if not item['discount_price']:
                item['discount_price'] = None
            else:
                item['discount_price'] = int(item['discount_price'][0].replace(' ', ''))
            # Если в значении price пустой список, то присваивается значение из discount_price
            if not item['price']:
                item['price'] = item['discount_price']
            else:
                item['price'] = int(item['price'][0].replace(' ', '').replace('р.', ''))

            # Рейтинг
            # Если в значении не пустой список, то приводится к float и делится на максимальную оценку на book24 (5)
            # Для приведения рейтингов на разных сайтах к единому виду
            if item['rating']:
                item['rating'] = float(item['rating'][0].replace(',', '.'))/5
            else:
                item['rating'] = None

        elif spider.name == 'labirint':
            item['title'] = item['title'].split(': ')[-1]

            # Проверка списка
            if item['authors']:
                # При длине равной 1, значение извлекается
                if len(item['authors']) == 1:
                    item['authors'] = item['authors'][0]
            else:
                item['authors'] = None

            item['price'] = int(item['price'])
            item['discount_price'] = int(item['discount_price'])

            # При рейтинге равном 0, присваивается None
            if float(item['rating']) == 0:
                item['rating'] = None
            # Приведение во float и деление на 10, для приведения к единому виду
            else:
                item['rating'] = float(item['rating'])/10

        collection = self.db[spider.name]
        collection.insert_one(item)
        return item
