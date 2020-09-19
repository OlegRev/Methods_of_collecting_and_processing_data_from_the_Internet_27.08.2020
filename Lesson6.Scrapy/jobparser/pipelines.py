# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient(
            "127.0.0.1: 27017",
            username="admin_vacancies",
            password="password_db",
            authSource="vacancies_db",
            authMechanism="SCRAM-SHA-1",
        )
        self.mongo_base = client["vacancies_db"]

    def process_item(self, item, spider):
        salary = item["salary"].replace("\xa0", "")
        salary = JobparserPipeline.restruct_compensation(salary)
        item["min_salary"] = salary["min_compensation"]
        item["max_salary"] = salary["max_compensation"]
        item["curency"] = salary["currency_compensation"]

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)

        return item

    @staticmethod
    def restruct_compensation(compensation: str):
        """Функция обработки укзателя зарплаты для
        разделения на минимальную, максимальную
        и денежную единицу измерения
        с использованием регулярных выражений
        (функция содержит import re)

        Args:
            compensation (str):
            тестировалось на выражениях:
                ['30000-70000 руб.', 'до 96000 руб.', 'от 150000 руб.',
                'от 150000 руб. до 200000 руб.', '200000-450000 KZT',
                '2500-4000 USD', '3000000', 'По договоренности' ,
                '30000-70000 руб./в месяц', '30000-70000 руб./в день'
                '3000-7000 руб./в час']
                            ]

        Returns:
            result (dict):
                result.keys(): [
                                'min_compensation',
                                'max_compensation',
                                'currency_compensation'
                            ]
        """
        import re

        if compensation.isdigit():
            result = {
                "min_compensation": int(compensation),
                "max_compensation": int(compensation),
                "currency_compensation": None,
            }
            return result

        elif re.search(r"^до", compensation):
            re_compensation = re.search(r"().*?(\d{1,}).*?(\w{3}).*?", compensation)
        elif "-" in compensation or ("от" in compensation and "до" in compensation):
            re_compensation = re.search(
                r".*?(\d{1,}).*?(\d{1,}).*?(\w{3}).*?", compensation
            )
        elif "от" in compensation and "до" not in compensation:
            re_compensation = re.search(r".*?(\d{1,}).*?()(\w{3}).*?", compensation)

        result = {
            "min_compensation": re_compensation.group(1),
            "max_compensation": re_compensation.group(2),
            "currency_compensation": re_compensation.group(3),
        }

        return result