# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class DataBasePipeline:
    def __init__(self):
        client = MongoClient('192.168.1.67', 27017)
        self.db = client['leroymerlin']

    def process_item(self, item, spider):
        # Название коллекции - поисковый запрос
        collection = self.db[spider.search]
        collection.insert_one(item)
        return item


class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    request = scrapy.Request(img)
                    # В meta записывается пара ключ-значение с названиием товара
                    request.meta['photo_dir'] = item['name']
                    yield request
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        # В названии может быть знак '/', который будет обработан как часть пути
        # Поэтому осуществляется замена на 'на'
        photo_dir = request.meta['photo_dir'].replace('/', ' на ')
        filename = request.url.split('/')[-1]
        return f'/{photo_dir}/{filename}'

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [i[1] for i in results if i[0]]
        print(1)
        return item
