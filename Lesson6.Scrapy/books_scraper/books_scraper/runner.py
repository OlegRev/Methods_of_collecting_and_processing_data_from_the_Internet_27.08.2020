from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from books_scraper import settings
from spiders.book24ru import Book24ruSpider
from spiders.labirintru import LabirintruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LabirintruSpider)
    process.crawl(Book24ruSpider)

    process.start()

