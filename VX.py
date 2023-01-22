import json
import os
import re

import requests
from jsonpath_ng import parse

from Data.Billboard import Cinema
from Model import models
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
                movie_title = re.search(r'[\w+\s+]+', str(item.name)).group(0)
                movie_poster_url = item.poster
                movie_year = re.search(r'\d+', str(item.year)).group(0)
                movie_len = re.search(r'\d+', str(item.length)).group(0)
                movie_country = ' '.join(map(str, re.findall(r'\w+', str(item.country))[1:]))
                movie_genre = re.search(r'\w+', str(item.genre)).group(0)
                movie_rating = re.search(r'\d+\.\d+', str(item.rating)).group(0)
                movie_id = re.search(r'\d+', str(item.film_id)).group(0)

                text = f'<b> {movie_title}</b>\n' \
                       f'Постер: {movie_poster_url}\n' \
                       f'Год производства: {movie_year}\n' \
                       f'Длительность: {movie_len} мин\n' \
                       f'Страна: {movie_country}\n' \
                       f'Жанр: {movie_genre}\n' \
                       f'Рейтинг по отзывам: {movie_rating}'
                with models.db:
                    movie = models.Movie(movie_id = movie_id,
                        movie_title=movie_title, movie_poster_url=movie_poster_url,
                                         movie_year=movie_year, movie_country=movie_country, movie_genre=movie_genre,
                                         movie_rating=movie_rating).save(force_insert=True)
                    print('Movie add')
                my_dict = {item.film_id: text}
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
