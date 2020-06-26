# -*- coding: utf-8 -*-
import scrapy
from bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    # поисковый запрос - программирование
    start_urls = ['https://book24.ru/search/?q=%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5']

    def parse(self, response):
        page_switchers = response.xpath("//a[@class='catalog-pagination__item _text js-pagination-catalog-item']")
        book_links = response.xpath("//a[@class='book__title-link js-item-element ddl_product_link ']/@href").extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        for switcher in page_switchers:
            if switcher.xpath("./text()").extract_first() == 'Далее':            # у кнопок "назад" и "далее" одинаковые классы
                next_page = switcher.xpath("./@href").extract_first()
                yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response):
        url = response.url
        title = response.xpath("//h1[@class='item-detail__title']/text()").extract_first()
        book_info = response.xpath("//div[@class='item-tab__chars-item']//text()").extract()
        price = response.xpath("//div[contains(@class, 'price-old')]/text()").extract()
        discount_price = response.xpath("//div[@class='item-actions__price']/b/text()").extract()
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract()

        yield BookparserItem(url=url,
                             title=title,
                             authors=book_info,
                             price=price,
                             discount_price=discount_price,
                             rating=rating)
