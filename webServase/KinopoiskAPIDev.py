import json
import os

import requests
from jsonpath_ng import parse


class KinopoiskAPIDev(object):
    __URL = 'https://api.kinopoisk.dev/movie'
    __KEY_API_KINOPOISK_DEV = os.getenv('KEY_API_KINOPOISK_DEV')

    def __get_json_by_url(self, url: str) -> dict:
        if not self.__KEY_API_KINOPOISK_DEV:
            raise Exception('Не импортировал токен для класса KinopoiskAPIDev')
        else:
            res = requests.get(url)
            if res.ok:
                return json.loads(res.text)

    def get_film_title_and_id(self, film_tile_query: str) -> [dict[str, str]]:
        url = self.__URL + '?token=' + self.__KEY_API_KINOPOISK_DEV + '&search=' + film_tile_query + '&field=name'
        json_data = self.__get_json_by_url(url)

        jsonpath_expression_id = parse('$..id')
        jsonpath_expression_name = parse('$..name')

        match_id = jsonpath_expression_id.find(json_data)
        match_name = jsonpath_expression_name.find(json_data)

        film_name = match_name[0].value
        film_id = match_id[0].value
        return {'film_name': film_name, 'film_id': film_id}
