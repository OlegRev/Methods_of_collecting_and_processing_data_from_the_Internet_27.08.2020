# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from re import search

import scrapy
from scrapy.loader.processors import Compose, MapCompose, TakeFirst


def retype_digit(item):
    """Функция выделения числового значения в тексте,
    с последующим преоброзованием в словарь с ключами:
        "digit" и "text"

    Args:
        item (str): Строка с числовыми значениями

    Returns:
        [dict]: .keys() -> "digit": ,"text": [description]
    """
    if search(r".*?\d{1,}.*?", item):
        if "." in item:
            re_item = search(r".*?(\d{1,}\.\d{1,}).*?", item)
        elif search(r".*?\d{1,}.*?", item):
            re_item = search(r".*?(\d{1,}).*?", item)
    else:
        re_item = {"digit": None, "text": item}
        return re_item
    result = {"digit": float(re_item.group(1)), "text": item}
    return result


def restruct_params(params):
    """Функция реструктурирования входящего списка в словарь по 2 элемента.

    Args:
        params ([type]): список параметров(характеристик товара)
        с сайта lroymerlin.ru

    Returns:
        [list]: Список кортежей по два элемента
    """
    __params = [itm.strip() for itm in params]
    __params = [itm for itm in __params if itm]
    __params = {
        __params[idx]: retype_digit(__params[idx + 1])
        for idx in range(0, len(__params), 2)
    }
    return __params


class LeruaMerlenItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    source = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(
        input_processor=MapCompose(float), output_processor=TakeFirst()
    )
    params = scrapy.Field(input_processor=Compose(restruct_params))
    _id = scrapy.Field()
