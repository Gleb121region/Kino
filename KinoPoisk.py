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
from converterStringDataToMinet import hms_to_s
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

    def __retrieve_value_by_key(self, json_data, jsonpath_x):
        return jsonpath_x.find(json_data)

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

                film_poster = self.__retrieve_value_by_key(json_data, parse('$.posterUrl'))
                film_rating = self.__retrieve_value_by_key(json_data, parse('$.ratingKinopoisk'))
                film_genre = self.__retrieve_value_by_key(json_data, parse('$.genres[*][*]'))
                film_country = self.__retrieve_value_by_key(json_data, parse('$.countries[*][*]'))
                film_len = self.__retrieve_value_by_key(json_data, parse('$.filmLength'))
                film_year = self.__retrieve_value_by_key(json_data, parse('$.year'))
                film_name = self.__retrieve_value_by_key(json_data, parse('$.nameRu'))

                list_film_genres = [genre.value['genre'] for genre in film_genre]
                list_film_counties = [country.value['country'] for country in film_country]

                if film_name:
                    cinema = Cinema(film_id=int(id_film),
                                    name=film_name[0].value,
                                    year=film_year[0].value,
                                    length=film_len[0].value,
                                    country=list_film_counties,
                                    genre=list_film_genres,
                                    rating=film_rating[0].value,
                                    poster=film_poster[0].value)
                    list_cinema.append(cinema)
                    tmp_id_film = id_film
        return list_cinema

    def set_id_kino_poisk(self, movie_name: str):
        movie_dict_list = Searcher().parse(query=movie_name)
        self.__id_kino_poisk = str(movie_dict_list[0]['film_id'])

    # добавлять в  БД
    def give_recommendations(self, movie_title: str) -> list[Film]:
        self.set_id_kino_poisk(movie_title)
        url: str = self.__URL + self.__id_kino_poisk + '/similars'
        json_data = self.__get_json_by_url(url)
        movies_title = self.__retrieve_value_by_key(json_data, parse('$.items[*].nameRu'))
        movies_id = self.__retrieve_value_by_key(json_data, parse('$.items[*].filmId'))
        list_films: list[Film] = []
        for movie_title, movie_id in zip(movies_title, movies_id):
            film_id = int(movie_id.value)
            film_name = movie_title.value
            description = self.__give_data_about_film(film_id)
            year = re.search(r"\d+", str(description.year)).group(0)
            length = re.search(r"\d+", str(description.length)).group(0)
            rating = re.search(r'\d+.\d+', str(description.rating)).group(0)
            poster = re.search(r'[\w:/.]+', str(description.poster)).group(0)
            country = description.country
            genre = description.genre

            add_movie(film_id, film_name, year, length, country, genre, rating, poster)

            country_write = ' '.join(map(str, re.findall(r'\w+', str(country))[1:]))
            genre_write = ' '.join(map(str, re.findall(r'\w+', str(genre))[1::2]))

            description = Description(poster, rating, year, country_write.replace('country', ''), genre_write, length)

            film_info = Film(film_name=film_name, film_id=film_id, description=description)

            list_films.append(film_info)
        return list_films

    def __give_data_about_film(self, id_kino_poisk: int) -> Description:
        url = self.__URL + str(id_kino_poisk)
        json_data = self.__get_json_by_url(url)

        poster = self.__retrieve_value_by_key(json_data, parse('$.posterUrl'))[0].value
        rating = self.__retrieve_value_by_key(json_data, parse('$.ratingKinopoisk'))[0].value
        year = self.__retrieve_value_by_key(json_data, parse('$.year'))[0].value
        data_duration = self.__retrieve_value_by_key(json_data, parse('$.filmLength'))[0].value
        list_counties = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.countries'))))
        list_genres = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.genres'))))

        data = Description(poster=poster,
                           rating=rating,
                           year=year,
                           country=list_counties,
                           genre=list_genres,
                           length=data_duration)
        return data

    def give_top_films(self, page_num: int) -> Billboard:
        url = self.__URL + f'top?page={page_num}'
        json_data = self.__get_json_by_url(url)

        list_film_id = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].filmId'))))
        list_film_name = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].nameRu'))))
        list_film_year = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].year'))))
        list_film_len = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].filmLength'))))
        list_film_country = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].countries'))))
        list_film_genre = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].genres'))))
        list_film_rating = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].rating'))))
        list_film_poster = list(
            map(lambda x: x.value, self.__retrieve_value_by_key(json_data, parse('$.films[*].posterUrl'))))

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
        obj = Billboard(list_movie)
        return obj

    def give_films_by_keyword(self, keyword: str, page_number: int):
        if keyword == '':
            raise ValueError('Empty keyword')
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={keyword}&page={page_number}'
        json_data = self.__get_json_by_url(url=url)
        film_id = self.__retrieve_value_by_key(json_data, parse('$.films[*].filmId'))
        film_name = self.__retrieve_value_by_key(json_data, parse('$.films[*].nameRu'))
        film_year = self.__retrieve_value_by_key(json_data, parse('$.films[*].year'))
        film_len = self.__retrieve_value_by_key(json_data, parse('$.films[*].filmLength'))
        film_country = self.__retrieve_value_by_key(json_data, parse('$.films[*].countries[*]'))
        film_genre = self.__retrieve_value_by_key(json_data, parse('$.films[*].genres'))
        film_rating = self.__retrieve_value_by_key(json_data, parse('$.films[*].rating'))
        film_poster = self.__retrieve_value_by_key(json_data, parse('$.films[*].posterUrl'))

        list_film_id = list(map(lambda x: x.value, film_id))
        list_film_name = list(map(lambda x: x.value, film_name))
        list_film_year = list(map(lambda x: x.value, film_year))
        list_film_len = list(map(lambda x: x.value, film_len))
        list_film_country = list(map(lambda x: x.value, film_country))
        list_film_genre = list(map(lambda x: x.value, film_genre))
        list_film_rating = list(map(lambda x: x.value, film_rating))
        list_film_poster = list(map(lambda x: x.value, film_poster))

        list_movie: list[Cinema] = []
        for film_id, name, year, length, country, genre, rating, poster in zip(list_film_id, list_film_name,
                                                                               list_film_year,
                                                                               list_film_len, list_film_country,
                                                                               list_film_genre, list_film_rating,
                                                                               list_film_poster):
            cinema: Cinema = Cinema(film_id=film_id, name=name, year=year, length=length, country=country, genre=genre,
                                    rating=rating, poster=poster)
            list_movie.append(cinema)
        obj = Billboard(list_movie)
        return obj

    def send_spin_offs(self, movie_name: str) -> list[Film]:
        self.set_id_kino_poisk(movie_name)
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/{int(self.__id_kino_poisk)}/sequels_and_prequels'
        json_data = self.__get_json_by_url(url=url)
        list_film_id = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data,parse('$..[filmId]'))))
        list_film_name = list(map(lambda x: x.value, self.__retrieve_value_by_key(json_data,parse('$..[nameRu]'))))
        list_film: list[Film] = []
        for film_id, name in zip(list_film_id, list_film_name):
            film: Film = Film(film_name=name, film_id=film_id, description=self.__give_data_about_film(film_id))
            list_film.append(film)
        return list_film
