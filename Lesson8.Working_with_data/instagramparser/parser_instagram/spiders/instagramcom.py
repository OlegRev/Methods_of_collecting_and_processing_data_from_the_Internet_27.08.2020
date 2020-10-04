# -*- coding: utf-8 -*-
from copy import deepcopy
import json
import re
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from graphql_query_hashs.graphql_query_hashs import (
    followers_query_hash,
    followquery_hashs,
    posts_query_hash,
)
from login_data import login_data_instagram
from parser_instagram.items import ParserInstagramItem


class InstagramcomSpider(scrapy.Spider):
    name = "instagramcom"
    allowed_domains = ["instagram.com"]
    start_urls = ["https://www.instagram.com/"]

    inst_login_link = "https://www.instagram.com/accounts/login/ajax/"
    insta_login = login_data_instagram.username
    insta_pwd = login_data_instagram.password
    # Пользователь, у которого собираем посты.
    # Можно указать список
    parse_user_list = [
        "python.russia",
        "rassbery.ru",
        "suse.linux",
        "raspberry_pi_builds",
    ]
    # ["geekbrains.ru", "ai_machine_learning", "python.learning"]
    graphql_url = "https://www.instagram.com/graphql/query/?"
    # hash для получения данных по постах с главной страницы
    posts_hash = posts_query_hash
    follow_hashs = followquery_hashs
    # Первый запрос на стартовую страницу

    def parse(self, response: HtmlResponse):
        # csrf token забираем из html
        csrf_token = self.fetch_csrf_token(response.text)
        # заполняем форму для авторизации
        yield scrapy.FormRequest(
            self.inst_login_link,
            method="POST",
            callback=self.user_parse,
            formdata={"username": self.insta_login, "enc_password": self.insta_pwd},
            headers={"X-CSRFToken": csrf_token},
        )

    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body["authenticated"]:  # Проверяем ответ после авторизации
            # Переходим на желаемую страницу пользователя.
            # Сделать цикл для кол-ва пользователей больше 2-ух
            for parse_user in self.parse_user_list:
                yield response.follow(
                    f"/{parse_user}",
                    callback=self.user_data_parse,
                    cb_kwargs={"username": parse_user},
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(
            response.text, username
        )  # Получаем id пользователя
        variables = {
            "id": user_id,  # Формируем словарь для передачи даных в запрос
            "first": 12,
        }  # 12 folow. 
        # Формируем ссылку для получения данных о постах

        for f_hash in self.follow_hashs:
            url_follow = f"{self.graphql_url}query_hash={f_hash}&{urlencode(variables)}"
            yield response.follow(
                url_follow,
                callback=self.user_follow_parse,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables),
                    "f_hash": deepcopy(f_hash),
                },
            )

    def user_follow_parse(
        self, response: HtmlResponse, username, user_id, variables, f_hash
    ):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        if f_hash == followers_query_hash:
            edges_follows = "edge_followed_by"
            follow_stat = "followers"
        else:
            edges_follows = "edge_follow"
            follow_stat = "following"
        page_info = j_data.get("data").get("user").get(edges_follows).get("page_info")
        if page_info.get("has_next_page"):  # Если есть следующая страница
            variables["after"] = page_info[
                "end_cursor"
            ]  # Новый параметр для перехода на след. страницу
            url_follow = f"{self.graphql_url}query_hash={f_hash}&{urlencode(variables)}"
            yield response.follow(
                url_follow,
                callback=self.user_follow_parse,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables),
                    "f_hash": deepcopy(f_hash),
                },
            )

        follow_ing_ers = (
            j_data.get("data").get("user").get(edges_follows).get("edges")
        )  # Сами  подписчики и подписки
        for (
            follow
        ) in follow_ing_ers:  # Перебираем подписчиков и подписок, собираем данные
            item = ParserInstagramItem(
                user_name=username,
                user_id=user_id,
                follow_stat=follow_stat,
                follow_id=follow["node"]["id"],
                follow_username=follow["node"]["username"],
                follow_full_name=follow["node"]["full_name"],
                follow_photo=follow["node"]["profile_pic_url"],
                follow=follow["node"],
            )
            yield item

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('"csrf_token":"\\w+"', text).group()
        return matched.split(":").pop().replace(r'"', "")

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search('{"id":"\\d+","username":"%s"}' % username, text).group()
        return json.loads(matched).get("id")
