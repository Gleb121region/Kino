import json
import os

import requests
from jsonpath_ng import parse

from KinoPoisk import KinoPoisk


class VX(object):
    URL = 'https://videocdn.tv/api/short'
    API_TOKEN = os.getenv('vx_token')

    def get_film_link_by_name(self, nameFilm: str) -> str:
        data = KinoPoisk()
        params = dict(api_token=self.API_TOKEN, kinopoisk_id=data.get_id_kino_poisk(nameFilm))
        res = requests.get(self.URL, params)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_expression = parse('$.data[*].iframe_src')
        match = jsonpath_expression.find(json_data)
        return str(match[0].value).replace("//", '')

    def get_film_by_kinopoisk_id(self, kinopoisk_id) -> str:
        params = dict(api_token=self.API_TOKEN, kinopoisk_id=kinopoisk_id)
        json_data = json.loads(requests.get(self.URL, params=params).text)
        jsonpath_expression = parse('$.data[*].iframe_src')
        match = jsonpath_expression.find(json_data)
        return str(match[0].value).replace("//", '')
