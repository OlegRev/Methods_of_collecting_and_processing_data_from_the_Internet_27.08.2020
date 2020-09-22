# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class LeruaMerlenPipeline:
    def __init__(self):
        DATABASE = "products_db"
        client = MongoClient(
            "127.0.0.1:27017",
            username="admin_products",
            password="password_db",
            authSource="products_db",
            authMechanism="SCRAM-SHA-1",
        )
        self.mongo_base = client[DATABASE]

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class LeruaMerlenPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["photos"]:
            for img in item["photos"]:
                try:
                    yield scrapy.Request(img, meta=item["name"])
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        product_name = request.meta["name"]
        directory = product_name
        file_name = request.url.split("/")[-1]
        return directory + "/" + file_name

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results if itm[0]]
        return item