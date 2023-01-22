import json
import os

import requests
from jsonpath_ng import parse

from Data.Billboard import Cinema
from kinoPoisk import KinoPoisk


class VX(object):
    __URL = 'https://videocdn.tv/api/short'
    __API_TOKEN = os.getenv('vx_token')

    def get_json_by_url(self, params: dict) -> str:
        return requests.get(self.__URL, params=params).text

    def get_film_link_by_name(self, name_film: str) -> list[dict]:
        list_kino_poisk: list[Cinema] = KinoPoisk().get_id_kino_poisk(name_film)
        list_links: list[dict] = []
        for item in list_kino_poisk:
            params = dict(api_token=self.__API_TOKEN, kinopoisk_id=item.film_id)
            json_string = self.get_json_by_url(params)
            json_data = json.loads(json_string)
            jsonpath_expression = parse('$.data[*].iframe_src')
            match = jsonpath_expression.find(json_data)
            if len(match) > 0:
                text = f'<b> {item.name}</b>\n' \
                       f'Постер: {item.poster}\n' \
                       f'Год производства: {item.year}\n' \
                       f'Длительность: {item.length} мин\n' \
                       f'Страна: {item.country}\n' \
                       f'Жанр: {item.genre}\n' \
                       f'Рейтинг по отзывам: {item.rating}' \
                    .replace('\'', '').replace("(", '').replace(")", '') \
                    .replace('{', '').replace('}', '').replace('[', '') \
                    .replace(']', '').replace(',', '').replace('country:', '').replace('country :', '')
                my_dict = {item.film_id:text}
                list_links.append(my_dict)
            else:
                return list_links
        return list_links

    def get_film_link_by_kinopoisk_id(self, kinopoisk_id: int) -> str | None:
        params = dict(api_token=self.__API_TOKEN, kinopoisk_id=kinopoisk_id)
        json_data = json.loads(self.get_json_by_url(params))
        jsonpath_expression = parse('$.data[*].iframe_src')
        match = jsonpath_expression.find(json_data)
        if len(match) > 0:
            return str(match[0].value).replace("//", '')
        else:
            return None
