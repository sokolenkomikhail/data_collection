'''1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
Для парсинга использовать xpath. Структура данных должна содержать:
название источника,
наименование новости,
ссылку на новость,
дата публикации'''

'''2)Сложить все новости в БД
'''

import requests
from lxml import html
from datetime import datetime, timedelta
from pymongo import MongoClient


def get_dom(link):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
    response = requests.get(link, headers=header)
    dom = html.fromstring(response.text)
    return dom


def news_dict(source, title, link, date):
    return {'source': source,
            'title': title,
            'link': link,
            'date': date}


def extract_first(lst):
    if lst:
        return lst[0]
    else:
        return None


def get_source_date(text):
    month_dict = {'января': '01',
                  'февраля': '02',
                  'марта': '03',
                  'апреля': '04',
                  'мая': '05',
                  'июня': '06',
                  'июля': '07',
                  'августа': '08',
                  'сентября': '09',
                  'октября': '10',
                  'ноября': '11',
                  'декабря': '12'}
    text = text.replace('\xa0', ' ')
    text_list = text.split()
    if text_list[-2] == 'в':
        if text_list[-3] == 'вчера':
            date = (datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')
            source = text.split(' вчера')[0]
        else:
            date = f'2020-{month_dict[text_list[-3]]}-{int(text_list[-4])}'
            source = text.rsplit(' ', maxsplit=4)[0]
    else:
        date = datetime.now().strftime('%Y-%m-%d')
        source = text[:-6]
    return source, date


def date_lenta(val):
    if val is not None:
        val = val.split('/')[2:5]
        val = '-'.join(val)
    return val


def parse_yandex_news():
    main_link = 'https://yandex.ru'
    href = '/news/rubric/business'
    dom = get_dom(main_link + href)
    blocks = dom.xpath("//div[contains(@class, 'story_view')]")
    news_list = []
    for block in blocks:
        source_string = extract_first(block.xpath(".//div[@class='story__date']/text()"))
        source, date = get_source_date(source_string)
        title = extract_first(block.xpath(".//h2[@class='story__title']/a/text()"))
        href = extract_first(block.xpath(".//h2[@class='story__title']/a/@href"))
        if href is not None:
            link = main_link + href
            news_link = extract_first(get_dom(link).xpath("//span[@class='story__head-agency']/a/@href"))
        else:
            news_link = None
        news = news_dict(source, title, news_link, date)
        news_list.append(news)
    return news_list


def parse_news_mail():
    main_link = 'https://news.mail.ru/economics/'
    dom = get_dom(main_link)
    blocks = dom.xpath(
        "//a[@class='newsitem__title link-holder'] | //a[@class='photo photo_small photo_scale photo_full grid__photo']"
    )
    news_list = []
    for block in blocks:
        link = extract_first(block.xpath('@href'))
        if link is not None:
            dom = get_dom(link)
            source = extract_first(dom.xpath("//span[@class='note']//span[@class='link__text']/text()"))
            date = extract_first(dom.xpath("//span[@datetime]/@datetime"))
            if date is not None:
                date = date.split('T')[0]
            title = extract_first(dom.xpath("//h1/text()"))
            news = news_dict(source, title, link, date)
            news_list.append(news)
    return news_list


def parse_lenta():
    main_link = 'https://lenta.ru'
    href = '/rubrics/economics'
    source = 'lenta.ru'
    dom = get_dom(main_link + href)
    blocks = dom.xpath("//section[@class='b-longgrid-column']//h3/a")
    news_list = []
    for block in blocks:
        href = extract_first(block.xpath("@href"))
        if href is not None:
            link = main_link + href
        else:
            link = None
        title = extract_first(block.xpath('./span/text()')).replace('\xa0', ' ')
        date = date_lenta(href)
        news = news_dict(source, title, link, date)
        news_list.append(news)
    return news_list


def insert_into_db(name, db, lst):
    collection = db[name]
    for el in lst:
        collection.insert_one(el)
    return collection


client = MongoClient('192.168.1.67', 27017)
news_db = client.news


insert_into_db('lenta', news_db, parse_lenta())
insert_into_db('yandex_news', news_db, parse_yandex_news())
insert_into_db('news_mail', news_db, parse_news_mail())
