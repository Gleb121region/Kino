import json
import os

import requests
from jsonpath_ng import parse

from Data.Billboard import Cinema
from KinoPoisk import KinoPoisk


class VX(object):
    URL = 'https://videocdn.tv/api/short'
    API_TOKEN = os.getenv('vx_token')

    def get_film_link_by_name(self, name_film: str) -> list[str]:
        list_kino_poisk: list[Cinema] = KinoPoisk().get_id_kino_poisk(name_film)
        list_links: list[str] = []
        for item in list_kino_poisk:
            params = dict(api_token=self.API_TOKEN, kinopoisk_id=item.film_id)
            res = requests.get(self.URL, params)
            json_string = res.text
            json_data = json.loads(json_string)
            jsonpath_expression = parse('$.data[*].iframe_src')
            match = jsonpath_expression.find(json_data)
            if len(match) > 0:
                url: str = str(match[0].value).replace("//", '')

                list_links.append(f'О кинопроизведении {item.name}\n'
                                       f'Ссылка на фильм: {url}\n'
                                       f'Постер: {item.poster}\n'
                                       f'Год производства: {item.year}\n'
                                       f'Длительность: {item.length}\n'
                                       f'Страна: {item.country}\n'
                                       f'Жанр: {item.genre}\n'
                                       f'Рейтинг по отзывам: {item.rating}'
                                       .replace("',)", '')
                                       .replace("('", '')
                                       )
            else:
                return list_links
            return list_links

    def get_film_by_kinopoisk_id(self, kinopoisk_id) -> str:
        params = dict(api_token=self.API_TOKEN, kinopoisk_id=kinopoisk_id)
        json_data = json.loads(requests.get(self.URL, params=params).text)
        jsonpath_expression = parse('$.data[*].iframe_src')
        match = jsonpath_expression.find(json_data)
        return str(match[0].value).replace("//", '')
