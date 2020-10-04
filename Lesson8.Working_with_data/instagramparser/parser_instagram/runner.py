from parser_instagram import settings
from parser_instagram.spiders.instagramcom import InstagramcomSpider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramcomSpider)
    process.start()
