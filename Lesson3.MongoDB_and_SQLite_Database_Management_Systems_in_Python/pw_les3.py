from my_parser import get_vacancies_list
from pymongo import MongoClient
from pprint import pprint

"""1) Развернуть у себя на компьютере/виртуальной машине/хостинге
MongoDB и реализовать функцию, записывающую собранные 
вакансии в созданную БД
2) Написать функцию, которая производит поиск 
и выводит на экран вакансии с заработной платой больше введенной суммы.
Поиск по двум полям (мин и макс зарплату)
3) Написать функцию, которая будет добавлять в вашу базу данных
только новые вакансии с сайта
"""


def get_digit(link:str):
    """Функция получения цифр из строки

    Args:
        link (str): [description]

    Returns:
       id_vacancy (str): [description]
    """
    from re import search
    re_link = search(r'.*?(\d{1,}).*?', link)
    id_vacancy = re_link.group(1)
    return id_vacancy

#1
def set_vacancies_to_mongo(client, db_name, collection_name, vacancies_list):
    db = client.db_name
    vacancies = db.collection_name
    vacancies_list = vacancies_list
    try:
        for vacancy in vacancies_list:
            vacancy['_id']= get_digit(vacancy['link'])
            vacancies.insert_one(vacancy)
        return "ok"
    except:
        return 'insert error'

#2
def find_vacancies(client, db_name, collection_name, upper_compensation):
    db = client.db_name
    vacancies = db.collection_name
    found_vacancies = vacancies.find({'$or': [{'min_compensation': {'$gt': upper_compensation}}, {'max_compensation': {'$gt': upper_compensation}}]})
    return found_vacancies

#3
def update_vacancies_to_mongo(client, db_name, collection_name, vacancies_list):
    db = client.db_name
    vacancies = db.collection_name
    vacancies_list = vacancies_list
    try:
        for vacancy in vacancies_list:
            vacancy['_id']= get_digit(vacancy['link'])
            vacancies.updata_many({'_id': vacancy['_id']}, {'$set': vacancy}, upsert=True)
        return "ok"
    except:
        return 'update error'

client = MongoClient('localhost', 27017)

required_vacancy = 'Data Scientist'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) ' 
               'Chrome/84.0.4147.135 Safari/537.36'}
db_name = 'vacancies_db'
collection_name = 'vacancies'
vacancies = get_vacancies_list(website_list=['hh.ru', 'superjob.ru'],
                              required_vacancy=required_vacancy,
                              headers=headers)

set_vacancies_to_mongo(client, db_name, collection_name, vacancies_list=vacancies)

pprint(find_vacancies(client, db_name, collection_name, 100000))

update_vacancies_to_mongo(client, db_name, collection_name, vacancies_list=vacancies)
