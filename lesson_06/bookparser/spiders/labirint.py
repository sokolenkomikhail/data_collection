# -*- coding: utf-8 -*-
import scrapy
from bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    # Поисковый запрос - программирование
    start_urls = ['https://www.labirint.ru/search/%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5/?available=1&wait=1&preorder=1&paperbooks=1&ebooks=1']

    def parse(self, response):
        book_links = response.xpath("//div[contains (@class, 'card-column')]/div/div/a[@class='product-title-link']/@href").extract()
        next_page = response.xpath("//a[@class='pagination-next__text']/@href").extract_first()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response):
        url = response.url
        title = response.xpath("//div[@id='product-title']/h1/text()").extract_first()
        authors = response.xpath("//div[@class='authors']/a[@data-event-label='author']/text()").extract()
        price = response.xpath("//span[@class='buying-priceold-val-number']/text()").extract_first()
        discount_price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()

        yield BookparserItem(url=url,
                             title=title,
                             authors=authors,
                             price=price,
                             discount_price=discount_price,
                             rating=rating)
