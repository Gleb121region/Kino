import json
import os
import re

import requests
from jsonpath_ng import parse

from Data.Billboard import Billboard
from Data.Cinema import Cinema
from Data.Description import Description
from Data.Film import Film
from DatabaseHandler import add_movie
from Text.regexText import regex_for_word, regex_for_url
from converterStringDataToMinet import hms_to_s
from jsonSearcher import retrieve_value_by_key
from searcherKinoPoisk import Searcher


class KinoPoisk(object):
    __URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
    __KEYS_KINO_POISK_API_UNOFFICIAL = os.getenv('KEYS_KINOPOISK_API_UNOFFICIAL').split()
    __id_kino_poisk = ''

    def __get_json_by_url(self, url: str) -> dict:
        if not self.__KEYS_KINO_POISK_API_UNOFFICIAL:
            raise Exception('Не импортировал токен для кино поиск api')
        for key in self.__KEYS_KINO_POISK_API_UNOFFICIAL:
            try:
                res = requests.get(url=url, headers={'X-API-KEY': key, 'Content-Type': 'application/json'})
                if res.ok:
                    return json.loads(res.text)
                else:
                    pass
            except (ConnectionError, json.JSONDecodeError) as error:
                print(error)

    def __give_data_about_film(self, id_kino_poisk: int) -> Description:
        json_data = self.__get_json_by_url(url=self.__URL + str(id_kino_poisk))
        list_country = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.countries'))))
        list_genre = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.genres'))))
        rating = retrieve_value_by_key(json_data, parse('$.ratingKinopoisk'))[0].value
        length = retrieve_value_by_key(json_data, parse('$.filmLength'))[0].value
        year = retrieve_value_by_key(json_data, parse('$.year'))[0].value
        if isinstance(rating, float) and isinstance(length, int) and isinstance(year, int):
            data = Description(
                poster=re.search(regex_for_url,
                                 retrieve_value_by_key(json_data, parse('$.posterUrl'))[0].value).group(0),
                rating=rating,
                year=year,
                country=' '.join(map(str, re.findall(regex_for_word, str(list_country))[1::2])),
                genre=' '.join(map(str, re.findall(regex_for_word, str(list_genre))[1::2])),
                length=length
            )
            return data
        else:
            raise ValueError('У фильма отсутствует длина год или рейтинг')

    def get_id_kino_poisk(self, movie_name: str) -> list[Cinema]:
        movie_list = Searcher().parse(movie_name)
        list_movie = [movie_dict['film_id'] for movie_dict in movie_list]
        return self.get_info_about_film_by_id_in_kino_poisk(list_movie)

    def get_info_about_film_by_id_in_kino_poisk(self, list_id_film: list[str]) -> list[Cinema]:
        list_cinema: list[Cinema] = []
        tmp_id_film = -1
        for id_film in (film_id for film_id in list_id_film if film_id is not None):
            if id_film != tmp_id_film:
                url = self.__URL + str(id_film)
                json_data = self.__get_json_by_url(url)
                film_name = retrieve_value_by_key(json_data, parse('$.nameRu'))
                if film_name:
                    film_country = retrieve_value_by_key(json_data, parse('$.countries[*][*]'))
                    film_genre = retrieve_value_by_key(json_data, parse('$.genres[*][*]'))
                    cinema = Cinema(film_id=int(id_film),
                                    name=film_name[0].value,
                                    year=retrieve_value_by_key(json_data, parse('$.year'))[0].value,
                                    length=retrieve_value_by_key(json_data, parse('$.filmLength'))[0].value,
                                    country=[country.value['country'] for country in film_country],
                                    genre=[genre.value['genre'] for genre in film_genre],
                                    rating=retrieve_value_by_key(json_data, parse('$.ratingKinopoisk'))[0].value,
                                    poster=retrieve_value_by_key(json_data, parse('$.posterUrl'))[0].value)
                    list_cinema.append(cinema)
                    tmp_id_film = id_film
        return list_cinema

    def set_id_kino_poisk(self, movie_name: str):
        movie_dict_list = Searcher().parse(query=movie_name)
        self.__id_kino_poisk = str(movie_dict_list[0]['film_id'])

    def give_recommendations(self, movie_title: str) -> list[Film]:
        self.set_id_kino_poisk(movie_title)
        url: str = self.__URL + self.__id_kino_poisk + '/similars'
        json_data = self.__get_json_by_url(url)
        movies_title = retrieve_value_by_key(json_data, parse('$.items[*].nameRu'))
        movies_id = retrieve_value_by_key(json_data, parse('$.items[*].filmId'))
        list_films: list[Film] = []
        for movie_title, movie_id in zip(movies_title, movies_id):
            film_id = int(movie_id.value)
            description = self.__give_data_about_film(film_id)
            film_name = movie_title.value
            add_movie(film_id, film_name, description.year, description.length, description.country, description.genre,
                      description.rating, description.poster)
            film_info = Film(film_name=film_name, film_id=film_id, description=description)
            list_films.append(film_info)
        return list_films

    def give_top_films(self, page_num: int) -> Billboard:
        url = self.__URL + f'top?page={page_num}'
        json_data = self.__get_json_by_url(url)

        list_film_id = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].filmId'))))
        list_film_name = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].nameRu'))))
        list_film_year = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].year'))))
        list_film_len = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].filmLength'))))
        list_film_country = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].countries'))))
        list_film_genre = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].genres'))))
        list_film_rating = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].rating'))))
        list_film_poster = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].posterUrl'))))

        list_movie: list[Cinema] = []
        for film_id, name, year, length, country, genre, rating, poster in zip(list_film_id, list_film_name,
                                                                               list_film_year,
                                                                               list_film_len, list_film_country,
                                                                               list_film_genre, list_film_rating,
                                                                               list_film_poster):
            length = hms_to_s(length)
            name = re.sub(r'·', '-', name)
            cinema: Cinema = Cinema(film_id=film_id, name=name, year=year, length=length,
                                    country=country, genre=genre, rating=rating, poster=poster)
            add_movie(film_id, name, year, length, country, genre, rating, poster)
            list_movie.append(cinema)
        return Billboard(list_movie)

    def give_films_by_keyword(self, keyword: str, page_number: int):
        if keyword == '':
            raise ValueError('Empty keyword')
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={keyword}&page={page_number}'
        json_data = self.__get_json_by_url(url=url)
        list_film_id = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].filmId'))))
        list_film_name = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].nameRu'))))
        list_film_year = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].year'))))
        list_film_len = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].filmLength'))))
        list_film_country = list(
            map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].countries[*]'))))
        list_film_genre = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].genres'))))
        list_film_rating = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].rating'))))
        list_film_poster = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$.films[*].posterUrl'))))

        list_movie: list[Cinema] = []
        for film_id, name, year, length, country, genre, rating, poster in zip(list_film_id, list_film_name,
                                                                               list_film_year,
                                                                               list_film_len, list_film_country,
                                                                               list_film_genre, list_film_rating,
                                                                               list_film_poster):
            cinema: Cinema = Cinema(film_id=film_id, name=name, year=year, length=length, country=country, genre=genre,
                                    rating=rating, poster=poster)
            add_movie(film_id, name, year, length, country, genre, rating, poster)
            if poster is not None and length is not None and rating is not None:
                list_movie.append(cinema)
        return Billboard(list_movie)

    def send_spin_offs(self, movie_name: str) -> list[Film]:
        self.set_id_kino_poisk(movie_name)
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/{int(self.__id_kino_poisk)}/sequels_and_prequels'
        json_data = self.__get_json_by_url(url=url)
        list_film_id = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$..[filmId]'))))
        list_film_name = list(map(lambda x: x.value, retrieve_value_by_key(json_data, parse('$..[nameRu]'))))
        list_film: list[Film] = []
        for film_id, name in zip(list_film_id, list_film_name):
            description = self.__give_data_about_film(film_id)
            film: Film = Film(film_name=name, film_id=film_id, description=description)
            add_movie(film_id, name, description.year, description.length, description.country, description.genre,
                      description.rating, description.poster)
            list_film.append(film)
        return list_film
