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
                res = requests.get(url, headers={'X-API-KEY': key, 'Content-Type': 'application/json'})
                if res.ok:
                    return json.loads(res.text)
                else:
                    pass
            except (ConnectionError, json.JSONDecodeError) as error:
                print(error)

    def __give_data_about_film(self, id_kino_poisk: int) -> Description:
        json_data = self.__get_json_by_url(url=self.__URL + str(id_kino_poisk))
        list_country = [x.value for x in retrieve_value_by_key(json_data, parse('$.countries'))]
        list_genre = [x.value for x in retrieve_value_by_key(json_data, parse('$.genres'))]
        rating = retrieve_value_by_key(json_data, parse('$.ratingKinopoisk'))[0].value
        length = retrieve_value_by_key(json_data, parse('$.filmLength'))[0].value
        year = retrieve_value_by_key(json_data, parse('$.year'))[0].value
        if isinstance(rating, float) and isinstance(length, int) and isinstance(year, int):
            poster = re.search(regex_for_url, retrieve_value_by_key(json_data, parse('$.posterUrl'))[0].value).group(0)
            data = Description(
                poster=poster,
                rating=rating,
                year=year,
                country=' '.join(map(str, re.findall(regex_for_word, str(list_country))[1::2])),
                genre=' '.join(map(str, re.findall(regex_for_word, str(list_genre))[1::2])),
                length=length
            )
            return data
        else:
            raise ValueError('У фильма отсутствует длина год или рейтинг')

    def __get_info_about_film_by_id_in_kino_poisk(self, list_id_film: list[str]) -> list[Cinema]:
        list_cinema: list[Cinema] = []
        tmp_id_film = -1
        for idx, id_film in enumerate(list_id_film):
            if idx == 0 or idx > 0 and idx != tmp_id_film:
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

    def get_id_kino_poisk(self, movie_name: str) -> list[Cinema]:
        movie_list = Searcher().parse(movie_name)
        list_movie = [movie_dict['film_id'] for movie_dict in movie_list]
        return self.__get_info_about_film_by_id_in_kino_poisk(list_movie)

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
            film_name = movie_title.value
            description = self.__give_data_about_film(film_id)
            print(description.genre)
            add_movie(film_id, film_name,
                      description.year, description.length,
                      description.country, description.genre,
                      description.rating, description.poster)
            film_info = Film(film_name=film_name, film_id=film_id, description=description)
            list_films.append(film_info)
        return list_films

    def give_top_films(self, page_num: int) -> Billboard:
        url = self.__URL + f'top?page={page_num}'
        json_data = self.__get_json_by_url(url)

        list_film_id = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].filmId'))]
        list_film_name = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].nameRu'))]
        list_film_year = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].year'))]
        list_film_len = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].filmLength'))]
        list_film_country = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].countries'))]
        list_film_genre = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].genres'))]
        list_film_rating = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].rating'))]
        list_film_poster = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].posterUrl'))]

        list_movie: list[Cinema] = []
        for i in range(len(list_film_id)):
            length, name = hms_to_s(list_film_len[i]), re.sub(r'[·–—]', '-', list_film_name[i])
            year, country, film_id = list_film_year[i], list_film_country[i], list_film_id[i]
            genre, rating, poster = list_film_genre[i], list_film_rating[i], list_film_poster[i]
            add_movie(film_id, name, year, length, country, genre, rating, poster)
            list_movie.append(Cinema(film_id=film_id, name=name, year=year, length=length,
                                     country=country, genre=genre, rating=rating, poster=poster))
        return Billboard(list_movie)

    def give_films_by_keyword(self, keyword: str, page_number: int):
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={keyword}&page={page_number}'
        json_data = self.__get_json_by_url(url)
        list_film_id = [x.value for x in retrieve_value_by_key(json_data, parse('$.films[*].filmId'))]
        list_cinema: list[Cinema] = self.__get_info_about_film_by_id_in_kino_poisk(list_film_id)
        list_cinema_clear: list[Cinema] = []
        for cinema in list_cinema:
            if isinstance(cinema.rating, float | int) and isinstance(cinema.length, int):
                list_cinema_clear.append(cinema)
                add_movie(cinema.film_id, cinema.name, cinema.year, cinema.length,
                          cinema.country, cinema.genre, cinema.rating, cinema.poster)
        return Billboard(list_cinema_clear)

    def send_spin_offs(self, movie_name: str) -> list[Film]:
        self.set_id_kino_poisk(movie_name)
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/{int(self.__id_kino_poisk)}/sequels_and_prequels'
        json_data = self.__get_json_by_url(url)
        list_film_id = [x.value for x in retrieve_value_by_key(json_data, parse('$..[filmId]'))]
        list_film_name = [x.value for x in retrieve_value_by_key(json_data, parse('$..[nameRu]'))]
        list_film: list[Film] = []
        for film_id, name in zip(list_film_id, list_film_name):
            description = self.__give_data_about_film(film_id)
            film: Film = Film(film_name=name, film_id=film_id, description=description)
            add_movie(film_id, name, description.year, description.length, description.country, description.genre,
                      description.rating, description.poster)
            list_film.append(film)
        return list_film
