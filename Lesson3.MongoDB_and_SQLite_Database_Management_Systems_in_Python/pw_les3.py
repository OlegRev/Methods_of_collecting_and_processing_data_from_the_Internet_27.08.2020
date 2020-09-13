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


#1
def set_vacancies_to_mongo(collection_name, vacancies_list):
    try:
        collection_name.insert_many(vacancies_list)
        return "ok"
    except:
        return 'insert error'

#2
def find_vacancies(collection_name, upper_compensation):

    found_vacancies = collection_name.find({'$or': [{'min_compensation': {'$gt': upper_compensation}}, {'max_compensation': {'$gt': upper_compensation}}]})
    return found_vacancies

#3
def update_vacancies_to_mongo(collection_name, vacancies_list):
    try:
        for vacancy in vacancies_list:
            collection_name.updata_many({'_id': vacancy['_id']}, {'$set': vacancy}, upsert=True)
        return "ok"
    except:
        return 'insert error'
       

required_vacancy = 'Программист python'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) ' 
                         'Chrome/84.0.4147.135 Safari/537.36'}

vacancies_list = get_vacancies_list(website_list=['hh.ru', 'superjob.ru'],
                                    required_vacancy=required_vacancy,
                                    headers=headers)

client = MongoClient('127.0.0.1:27017',
                     username='admin_vacancies',
                     password='password_db',
                     authSource='vacancies_db',
                     authMechanism='SCRAM-SHA-1')


db = client['vacancies_db']
collection = db.vacancies

try:
    set_vacancies_to_mongo(collection_name=collection, vacancies_list=vacancies_list[:100])
    print('ok')
except:
    print('error')
    
try:
    for vacancy in find_vacancies(collection_name=collection, upper_compensation=100000 ):
        pprint(vacancy)
    print('ok')
except:
    print('find error')

try:
    update_vacancies_to_mongo(collection_name=collection, vacancies_list=vacancies_list)
    print('ok')
except:
    print('update error')
