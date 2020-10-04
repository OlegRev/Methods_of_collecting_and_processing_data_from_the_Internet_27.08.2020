# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParserInstagramItem(scrapy.Item):
    # define the fields for your item here like:

    user_name = scrapy.Field()
    user_id = scrapy.Field()
    follow_stat = scrapy.Field()
    follow_id = scrapy.Field()
    follow_username = scrapy.Field()
    follow_full_name = scrapy.Field()
    follow_photo = scrapy.Field()
    follow = scrapy.Field()
    _id = scrapy.Field()
