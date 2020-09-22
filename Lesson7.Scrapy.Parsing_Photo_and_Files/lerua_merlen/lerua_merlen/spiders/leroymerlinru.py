import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from ..items import LeruaMerlenItem


class LeroymerlinruSpider(scrapy.Spider):
    name = "leroymerlinru"
    allowed_domains = ["leroymerlin.ru"]

    def __init__(self, search):
        self.start_urls = [f"https://spb.leroymerlin.ru/search/?q={search}"]
        self.query = search

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@slot="name"]')
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)
        try:
            next_page = response.xpath('//a[@rel="next"]/@href').get()
            yield response.follow(next_page, callback=self.parse)
        except:
            pass

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaMerlenItem(), response=response)

        loader.add_value("link", response.url)

        loader.add_xpath("name", "//h1/text()")

        loader.add_xpath("price", '//span[@slot="price"]/text()')

        loader.add_xpath(
            "photos", '//source[contains(@data-origin, "2000")]/@data-origin'
        )

        loader.add_xpath("params", '//div[@class="def-list__group"]//text()')

        yield loader.load_item()
