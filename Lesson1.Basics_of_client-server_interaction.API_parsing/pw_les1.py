import requests
import json
from config import TOKEN

user_name = "OlegRev"

def user_repos_in_github(user_name:str):
    """
    Функция(1.1) вывода имен репозиториев заданного
        пользователя и записи в файл .json вывода 

        Функция принимает user_name:str : 
            Имя пользователя в github().
        Результатом функции является: 
            файл user_data.json,
            список репозиториев поьзователя user_repos
        
    """
    service = "https://api.github.com/"
    req = requests.get(f'{service}users/{user_name}/repos')
    data = json.loads(req.text)
    with open("./user_data.json", "w") as write_file:
        json.dump(data, write_file)
    user_repos = [repo['name'] for repo in data]
    return user_repos


def tg_bot_name():
    """ Функция 1.2 Изучить список открытых API.
        Найти среди них любое, требующее авторизацию
        (любого типа). 
        Выполнить запросы к нему, пройдя авторизацию.
        Ответ сервера записать в файл.

        Функция возвращает имя телеграм бота 
            и сохраняет в файл bot_data.json 
            вывод метода getMe из Telegram Bot API
    """ 
    service = "https://api.telegram.org/bot"
    req = requests.get(f'{service}{TOKEN}/getMe')
    bot_data = json.loads(req.text)
    with open("./bot_data.json", "w") as write_file:
        json.dump(bot_data, write_file)
    bot_name = bot_data['result']['first_name']
    return bot_name  


for repo_name in user_repos_in_github(user_name):
    print(repo_name)

print(tg_bot_name())
