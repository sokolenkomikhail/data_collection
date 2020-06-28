# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst
from lxml import html
import scrapy


def price_processing(value):
    if value:
        value = value.replace(' ', '')
        if value.isdigit():
            return int(value)
        else:
            return value
    else:
        return None


def specs_processing(raw_specs):
    if raw_specs:
        dom = html.fromstring(raw_specs)
        # ключи из таблицы спецификации товара
        specs_keys = dom.xpath('./div/dt/text()')
        # значения из таблицы спецификации товара
        specs_values = dom.xpath('./div/dd/text()')
        specs_values = [i.replace('\n', '').replace('  ', '') for i in specs_values]
        # приведение значений к соответствующим типам данных
        for i, val in enumerate(specs_values):
            # проверка - является ли элемент числовым
            if val.isdigit():
                specs_values[i] = int(val)
            # к остальным применяется метод partition
            else:
                partition = val.partition('.')
                # проверяется вхождение элемента '.' в полученный кортеж
                if '.' in partition:
                    # если первый и третий (последний) элементы кортежа являются числовыми, то приводится к float
                    if partition[0].isdigit() and partition[-1].isdigit():
                        specs_values[i] = float(val)
        # сборка словаря из списков ключей и значений
        specs = dict(zip(specs_keys, specs_values))
        return specs
    else:
        return None


class LeroymerlinparserItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    specs = scrapy.Field(input_processor=MapCompose(specs_processing), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(price_processing), output_processor=TakeFirst())
