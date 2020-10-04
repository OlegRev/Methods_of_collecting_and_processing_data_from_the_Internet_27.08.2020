# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient


class ParserInstagramPipeline:
    def __init__(self):
        DATABASE = "instagram_db"
        client = MongoClient(
            "127.0.0.1:27017",
            username="admin_instagram",
            password="password_db",
            authSource="instagram_db",
            authMechanism="SCRAM-SHA-1",
        )
        self.mongo_base = client[DATABASE]

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
