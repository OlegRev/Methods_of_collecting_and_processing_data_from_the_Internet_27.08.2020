# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from pymongo import MongoClient


class BooksScraperPipeline:
    def __init__(self):
        client = MongoClient(
            "127.0.0.1:27017",
            username="admin_books",
            password="password_db",
            authSource="books_db",
            authMechanism="SCRAM-SHA-1",
        )

        self.mongo_base = client["books_db"]

    def process_item(self, item, spider):

        link_to_book = item["link_to_book"]
        book_title = item["book_title"]
        author = item["author"]
        basic_price = item["basic_price"]
        discount_price = item["discount_price"]
        price = item["price"]

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        return item
