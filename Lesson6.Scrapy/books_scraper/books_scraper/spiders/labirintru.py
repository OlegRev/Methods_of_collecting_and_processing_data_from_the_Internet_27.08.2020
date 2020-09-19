import scrapy
from scrapy.http import HtmlResponse

from books_scraper.items import BooksScraperItem


class LabirintruSpider(scrapy.Spider):
    name = "labirintru"
    allowed_domains = ["labirint.ru"]
    start_urls = ["http://https://www.labirint.ru/books/"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="pagination-next__text"]/@href').get()
        books_link = response.xpath(
            '//div[@id="catalog"]//div[@class="product-cover"]'
            '//a[@class="product-title-link"]/@href'
        ).getall()
        for link in books_link:
            yield response.follow(link, callback=self.book_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link_to_book = response.url
        book_title = response.xpath("//h1/text()").get()
        author = response.xpath('//div[@class="authors"]/a/text()').get()
        basic_price = response.xpath(
            '//span[@class="buying-priceold-val-number"]/text()'
        ).get()
        discount_price = response.xpath(
            '//span[@class="buying-pricenew-val-number"]/text()'
        ).get()
        price = response.xpath(
            '//span[@class="buying-price-val-number"]/text()'
        ).get()
        book_rating = response.xpath('//div[@id="rate"]/text()').get()
        yield BooksScraperItem(
            link_to_book=link_to_book,
            book_title=book_title,
            author=author,
            basic_price=basic_price,
            discount_price=discount_price,
            price=price,
            book_rating=book_rating,
        )
