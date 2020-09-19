import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = "hhru"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://izhevsk.hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=python&showClusters=true"
    ]

    def parse(self, response: HtmlResponse):
        vacancies = response.css(
            "div.vacancy-serp-item__row_header a.bloko-link::attr(href)"
        ).extract()
        for vacancy in vacancies:
            yield response.follow(vacancy, callback=self.vacancy_parse)

        next_page = response.css("a.HH-Pager-Controls-Next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']//text()").getall()
        page_link = response.url
        yield JobparserItem(name=name, salary=salary, page_link=page_link)
