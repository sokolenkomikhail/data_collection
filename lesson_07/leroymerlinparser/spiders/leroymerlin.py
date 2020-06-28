import scrapy
from leroymerlinparser.items import LeroymerlinparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']
        # Атрибут для передачи в DataBasePipeline
        self.search = search

    def parse(self, response):
        # На странице 2 кнопки для перехода на след страницу. В верхней и нижней части
        # Поэтому применен метод extract_first()
        next_page = response.xpath("//a[@class='paginator-button next-paginator-button']/@href").extract_first()
        goods_links = response.xpath("//a[@class='black-link product-name-inner']")
        for link in goods_links:
            yield response.follow(link, callback=self.parse_goods)
        yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath("name", "//h1/text()")
        loader.add_xpath("photos", "//img[@alt='product image']/@src")
        loader.add_xpath("specs", "//dl[@class='def-list']")
        loader.add_value("url", response.url)
        loader.add_xpath("price", "//uc-pdp-price-view[@class='primary-price']/span[@slot='price']/text()")
        yield loader.load_item()
