"""Написать приложение,
 которое собирает основные новости с сайтов:
    mail.ru,
    lenta.ru,
    yandex-новости.
 Для парсинга использовать XPath.
 Структура данных должна содержать:

    название источника;
    наименование новости;
    ссылку на новость;
    дата публикации.

Сложить все в базу данных
"""
from pprint import pprint
from lxml import html
import requests
import datetime
from pymongo import MongoClient, errors



def get_news(website: str, rubric: str):
    """
    website == 'mail.ru' ,
               'lenta.ru',
               'yandex.ru'
              
    rubric == 'politics',
              'economics',
              'society',
              'incident'
    """
    rubric_dict = {'politics': 0, 'economics': 1, 'society': 2, 'incident': 3}
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
    links_for_news = {'mail.ru' : {'main_link': 'https://news.mail.ru',
                                   'second_link': ['/politics/', '/economics/', '/society/', '/incident/']},
                      'lenta.ru': {'main_link': 'https://lenta.ru',
                                   'second_link': ['/rubrics/world/politic/', '/rubrics/economics/', '/rubrics/world/society/', '/rubrics/world/accident/']},
                      'yandex.ru': {'main_link': 'https://yandex.ru/news',
                                    'second_link': ['/rubric/politics', '/rubric/business', '/rubric/society', '/rubric/incident']}
                     }

    news_link_xpath = {'mail.ru' : "//div[@data-module='TrackBlocks']//a[contains(@href, 'news.mail.ru') and not(contains(@href, 'comments'))]/@href",
                       'lenta.ru': "//section[contains(@class, 'rubric')]//a[@href and not(contains(@class, 'banner-pay'))]/@href",
                       'yandex.ru': "//article[contains(@class, 'news-card')]//a[@class='news-card__link']/@href"}
    news_name_xpath = {'mail.ru' : "//div[@data-module='TrackBlocks']/div[contains(@class,'hdr') and contains(@class,'title')]//h1",
                       'lenta.ru': "//div[contains(@class,'b-topic-layout')]//h1",
                       'yandex.ru': "//article[contains(@class, 'news-card')]//a[@class='news-card__link']/h2"}
    date_of_publication_xpath = {'mail.ru' : "//div[@data-module='TrackBlocks']/div[contains(@class,'breadcrumbs')]//span[@datetime]/@datetime",
                                 'lenta.ru': "//div[contains(@class,'b-topic-layout')]//time[@class='g-date']/@datetime",
                                 'yandex.ru': "//article[contains(@class, 'news-card')]//span[@class='mg-card-source__time']"}                           
    news_source_link_xpath = {'mail.ru' : "//div[@data-module='TrackBlocks']/div[contains(@class,'breadcrumbs')]//a[@target]/@href",
                              'lenta.ru': "https://lenta.ru",
                              'yandex.ru': "//article[contains(@class, 'news-card')]//div[contains(@class, 'news-card__source')]/span/a[@href]/@href"}
    news_source_name_xpath = {'mail.ru' : "//div[@data-module='TrackBlocks']/div[contains(@class,'breadcrumbs')]//a[@target]/span[@class='link__text']",
                              'lenta.ru': "Lenta.ru («Лента.ру»)",
                              'yandex.ru': "//article[contains(@class, 'news-card')]//div[contains(@class, 'news-card__source')]//a/text()"}
    
    link = links_for_news[website]['main_link'] + links_for_news[website]['second_link'][rubric_dict[rubric]]
    request = requests.get(link, headers=headers)
    root_dom = html.fromstring(request.text)
    news_links = root_dom.xpath(news_link_xpath[website])
    news_data = []
    if website == 'yandex.ru':
        news_name = root_dom.xpath(news_name_xpath[website])
        date_of_publication = root_dom.xpath(date_of_publication_xpath[website])
        news_source_link = root_dom.xpath(news_source_link_xpath[website])
        news_source_name = root_dom.xpath(news_source_name_xpath[website])
        for link_item in  range(len(news_links)):
            news = {}
            news['news_link'] = news_links[link_item]
            news['news_name'] = news_name[link_item].text
            __date_news = datetime.date.today()
            news['date_of_publication'] =   [f'{str(__date_news)} {date_of_publication[link_item].text}']
            request = requests.get(news_source_link[link_item], headers=headers)
            root_dom = html.fromstring(request.text)
            news['news_source_link'] = root_dom.xpath("//a[@class='news-story__subtitle']/@href")[0]
            news['news_source_name'] = news_source_name[link_item]
            news_data.append(news)
        return news_data
    
    for link_item in set(news_links):
        news = {}
        if website == 'lenta.ru':
            link_item = links_for_news[website]['main_link'] + link_item
        request = requests.get(link_item, headers=headers)
        root_dom = html.fromstring(request.text)
        
        news_name = root_dom.xpath(news_name_xpath[website])
        date_of_publication = root_dom.xpath(date_of_publication_xpath[website])
        
        news['news_link'] = link_item
        news['date_of_publication'] = date_of_publication
        if website == 'mail.ru':
            news['news_name'] = news_name[0].text
            
            news_source_link = root_dom.xpath(news_source_link_xpath[website])
            news_source_name = root_dom.xpath(news_source_name_xpath[website])
            news['news_source_link'] = news_source_link[0]
            news['news_source_name'] = news_source_name[0].text
        elif website == 'lenta.ru':        
            news['news_name'] = news_name[0].text.replace('\xa0', ' ')  
            news['news_source_link'] = news_source_link_xpath[website]
            news['news_source_name'] = news_source_name_xpath[website]
        
        news_data.append(news)
        
    return news_data
        



if __name__ == "__main__":
    news_data = []
    news_data.extend(get_news('mail.ru', rubric='politics'))
    news_data.extend(get_news('lenta.ru', rubric='politics'))
    news_data.extend(get_news('yandex.ru', rubric='politics')
    client = MongoClient('127.0.0.1:27017',
                         username='admin_news',
                         password='password_db',
                         authSource='news_db',
                         authMechanism='SCRAM-SHA-1')
    

    db = client['news_db']
    collection = db.news

    count = 0
    for item_news in data_insert:
        try:
            collection.insert_one(item_news)
            count += 1
        except errors.DuplicateKeyError:
            print("Errdor DuplicateKeyError")

    print(count)
