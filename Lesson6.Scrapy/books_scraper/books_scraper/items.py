# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    link_to_book = scrapy.Field()
    book_title = scrapy.Field()
    author = scrapy.Field()
    basic_price = scrapy.Field()
    discount_price = scrapy.Field()
    price = scrapy.Field()
