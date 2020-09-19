import scrapy
from scrapy.http import HtmlResponse

from books_scraper.items import BooksScraperItem


class Book24ruSpider(scrapy.Spider):
    name = "book24ru"
    allowed_domains = ["book24.ru"]
    start_urls = ["https://book24.ru/catalog/"]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            '//div[@class="catalog-pagination__list"]//a[contains(@class, "_text")]/@href'
        ).get()
        books_link = response.xpath(
            '//div[@class="catalog-products"]//a[@data-element="title"]/@href'
        ).getall()
        for link in books_link:
            yield response.follow(link, callback=self.book_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link_to_book = response.url
        book_title = response.xpath("//h1/text()").get()
        author = response.xpath(
            '//span[@class="item-tab__chars-value"]/a[contains(@href, "author")]/text()'
        ).get()
        basic_price = response.xpath(
            '//div[@class="item-actions__price-old"]/b/text()'
        ).get()
        discount_price = response.xpath(
            '//div[@class="item-actions__price"]/b/text()'
        ).get()
        price = response.xpath('//div[@class="item-actions__price"]/b/text()').get()
        book_rating = response.xpath('//span[@class="rating__rate-value"]/text()').get()

        yield BooksScraperItem(
            link_to_book=link_to_book,
            book_title=book_title,
            author=author,
            basic_price=basic_price,
            discount_price=discount_price,
            price=price,
            book_rating=book_rating,
        )
