import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = "superjobru"
    allowed_domains = ["   superjob.ru"]
    start_urls = ["https://russia.superjob.ru/vacancy/search/?keywords=python"]

    def parse(self, response: HtmlResponse):
        vacancies = response.xpath(
            '//div[@class="_3mfro PlM3e _2JVkc _3LJqf"]/a/@href'
        ).extract()
        for vacancy in vacancies:
            yield response.follow(vacancy, callback=self.vacancy_parse)

        next_page = response.css('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").getall()
        salary = response.xpath('//span[@class="_1OuF_ ZON4b"]//text()').getall()
        page_link = response.url
        yield JobparserItem(name=name, salary=salary, page_link=page_link)
