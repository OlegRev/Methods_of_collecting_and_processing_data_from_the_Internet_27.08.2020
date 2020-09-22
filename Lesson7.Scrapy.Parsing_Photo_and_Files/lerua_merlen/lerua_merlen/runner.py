from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from ..lerua_merlen import settings
from ..lerua_merlen.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == "__main__":

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search="Линолеум")

    process.start()
