import json
import os
import re

import requests
from jsonpath_ng import parse

from Data.Billboard import Cinema
from Text.messagesPattern import stencil


class VX(object):
    __URL = 'https://videocdn.tv/api/short'
    __API_TOKEN = os.getenv('vx_token')

    def get_json_by_url(self, params: dict) -> str:
        return requests.get(self.__URL, params=params).text

    def get_film_link_by_name(self, name_film: str) -> list[dict]:
        from KinoPoisk import KinoPoisk
        list_kino_poisk: list[Cinema] = KinoPoisk().get_id_kino_poisk(name_film)
        list_links: list[dict] = []
        for item in list_kino_poisk:
            params = dict(api_token=self.__API_TOKEN, kinopoisk_id=item.film_id)
            json_string = self.get_json_by_url(params)
            json_data = json.loads(json_string)
            jsonpath_expression = parse('$.data[*].iframe_src')
            match = jsonpath_expression.find(json_data)
            if len(match) > 0:
                movie_title = item.name
                movie_poster_url = item.poster
                movie_year = item.year
                movie_len = item.length
                movie_country = re.sub(r'[(\[\'\])]', '', str(item.country))
                movie_genre = re.sub(r'[(\[\'\])]', '', str(item.genre))
                movie_rating = item.rating
                text = stencil(item.name, movie_poster_url, movie_year, movie_len, movie_country, movie_genre,
                               movie_rating)
                movie_id = re.search(r'\d+', str(item.film_id)).group(0)
                movie_video_url = self.get_film_link_by_kinoP_id(int(movie_id))
                from DatabaseHandler import add_movie
                add_movie(film_id=movie_id,
                          name=movie_title.lower().capitalize(),
                          poster=movie_poster_url,
                          length=movie_len,
                          year=movie_year,
                          country=movie_country,
                          genre=movie_genre,
                          rating=movie_rating)
                my_dict = {movie_video_url: text}
                list_links.append(my_dict)
            else:
                return list_links
        return list_links

    def get_film_link_by_kinoP_id(self, kinoP_id: int) -> str | None:
        params = dict(api_token=self.__API_TOKEN, kinopoisk_id=kinoP_id)
        json_data = json.loads(self.get_json_by_url(params))
        jsonpath_expression = parse('$.data[*].iframe_src')
        match = jsonpath_expression.find(json_data)
        if len(match) > 0:
            return str(match[0].value)[2:]
        else:
            return None
