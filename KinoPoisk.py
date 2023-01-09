import json
import os

import requests
from jsonpath_ng import parse

from Data.Billboard import Billboard
from Data.Cinema import Cinema
from Data.Description import Description
from Data.Film import Film
from SearcherKinoPoisk import Searcher


class KinoPoisk(object):
    URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
    API_TOKEN = os.getenv('kino_poisk_token')
    headers = {'X-API-KEY': API_TOKEN, 'Content-Type': 'application/json'}
    id_kino_poisk = ''

    def get_id_kino_poisk(self, movie_name: str) -> list[Cinema]:
        movie_list = Searcher().parse(movie_name)
        list_movie = []
        for movie_dict in movie_list:
            if movie_dict['film_name'].casefold() == movie_name.casefold():
                list_movie.append(movie_dict['film_id'])
        list_movie_info = self.get_info_about_film_by_id_in_kino_poisk(list_id_film=list_movie)
        return list_movie_info

    def get_info_about_film_by_id_in_kino_poisk(self, list_id_film: list[str]) -> list[Cinema]:
        list_cinema: list[Cinema] = []
        for id_film in list_id_film:
            url = self.URL + str(id_film)
            res = requests.get(url=url, headers=self.headers)
            json_string = res.text
            json_data = json.loads(json_string)

            jsonpath_name = parse('$.nameRu')
            jsonpath_year = parse('$.year')
            jsonpath_len = parse('$.filmLength')
            jsonpath_country = parse('$.countries[*]')
            jsonpath_genre = parse('$.genres[*][*]')
            jsonpath_rating = parse('$.ratingKinopoisk')
            jsonpath_poster = parse('$.posterUrl')

            film_poster = jsonpath_poster.find(json_data)
            film_rating = jsonpath_rating.find(json_data)
            film_genre = jsonpath_genre.find(json_data)
            film_country = jsonpath_country.find(json_data)
            film_len = jsonpath_len.find(json_data)
            film_year = jsonpath_year.find(json_data)
            film_name = jsonpath_name.find(json_data)

            list_film_genre = []

            for genre in film_genre:
                list_film_genre.append(genre.value['genre'])

            cinema = Cinema(film_id=int(id_film), name=film_name[0].value, year=film_year[0].value,
                            length=film_len[0].value, country=film_country[0].value, genre=list_film_genre,
                            rating=film_rating[0].value, poster=film_poster[0].value)
            list_cinema.append(cinema)
        return list_cinema

    def set_id_kino_poisk(self, movie_name: str):
        movie_dict_list = Searcher().parse(query=movie_name)
        self.id_kino_poisk = str(movie_dict_list[0]['film_id'])

    def give_recommendations(self, name: str) -> list[Film]:
        self.set_id_kino_poisk(name)
        url: str = self.URL + self.id_kino_poisk + '/similars'
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_name = parse('$.items[*].nameRu')
        jsonpath_film_id = parse('$.items[*].filmId')
        names = jsonpath_name.find(json_data)
        ids = jsonpath_film_id.find(json_data)
        list_films: list[Film] = []
        for name, id_string in zip(names, ids):
            film_info = Film(film_name=name.value,
                             film_id=int(id_string.value),
                             description=self.give_data_about_film(int(id_string.value)))
            list_films.append(film_info)
        return list_films

    def give_data_about_film(self, id_kino_poisk: int) -> Description:
        url = self.URL + str(id_kino_poisk)
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)

        jsonpath_poster = parse('$.posterUrl')
        posters = jsonpath_poster.find(json_data)
        poster = posters[0].value

        jsonpath_rating = parse('$.ratingKinopoisk')
        ratings = jsonpath_rating.find(json_data)
        rating = ratings[0].value

        jsonpath_year = parse('$.year')
        years = jsonpath_year.find(json_data)
        year = years[0].value

        jsonpath_description = parse('$.description')
        descriptions = jsonpath_description.find(json_data)
        description_data = descriptions[0].value

        jsonpath_type = parse('$.type')
        types = jsonpath_type.find(json_data)
        data_type = types[0].value

        jsonpath_county = parse('$.countries[*].country')
        counties = jsonpath_county.find(json_data)
        list_counties = list(map(lambda x: x.value, counties))

        jsonpath_genres = parse('$.genres[*].genre')
        genres = jsonpath_genres.find(json_data)
        list_genres = list(map(lambda x: x.value, genres))

        jsonpath_filmLength = parse('$..filmLength')
        duration = jsonpath_filmLength.find(json_data)
        data_duration = duration[0].value

        jsonpath_start_year = parse('$.startYear')
        start_years = jsonpath_start_year.find(json_data)
        start_year = start_years[0].value

        jsonpath_end_year = parse('$.endYear')
        end_years = jsonpath_end_year.find(json_data)
        end_year = end_years[0].value

        data = Description(poster=poster,
                           rating=rating,
                           year=year,
                           description=description_data,
                           type=data_type,
                           countries=list_counties,
                           genres=list_genres,
                           start_year=start_year,
                           end_year=end_year,
                           duration=data_duration)
        return data

    def give_top_films(self, page_num: int) -> Billboard:
        url = self.URL + f'top?page={page_num}'
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)

        jsonpath_film_id = parse('$.films[*].filmId')
        film_id = jsonpath_film_id.find(json_data)
        jsonpath_name = parse('$.films[*].nameRu')
        film_name = jsonpath_name.find(json_data)
        jsonpath_year = parse('$.films[*].year')
        film_year = jsonpath_year.find(json_data)
        jsonpath_film_len = parse('$.films[*].filmLength')
        film_len = jsonpath_film_len.find(json_data)
        jsonpath_country = parse('$.films[*].countries[*]')
        film_country = jsonpath_country.find(json_data)
        jsonpath_genre = parse('$.films[*].genres')
        film_genre = jsonpath_genre.find(json_data)
        jsonpath_rating = parse('$.films[*].rating')
        film_rating = jsonpath_rating.find(json_data)
        jsonpath_poster = parse('$.films[*].posterUrl')
        film_poster = jsonpath_poster.find(json_data)

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
            cinema: Cinema = Cinema(film_id=film_id,
                                    name=name,
                                    year=year,
                                    length=length,
                                    country=country,
                                    genre=genre,
                                    rating=rating,
                                    poster=poster)
            list_movie.append(cinema)
        obj = Billboard(list_movie)
        return obj

    def give_films_by_keyword(self, keyword: str, page_number: int):
        if keyword == '':
            raise ValueError('Empty keyword')
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={keyword}&page={page_number}'
        res = requests.get(url=url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_film_id = parse('$.films[*].filmId')
        film_id = jsonpath_film_id.find(json_data)
        jsonpath_name = parse('$.films[*].nameRu')
        film_name = jsonpath_name.find(json_data)
        jsonpath_year = parse('$.films[*].year')
        film_year = jsonpath_year.find(json_data)
        jsonpath_film_len = parse('$.films[*].filmLength')
        film_len = jsonpath_film_len.find(json_data)
        jsonpath_country = parse('$.films[*].countries[*]')
        film_country = jsonpath_country.find(json_data)
        jsonpath_genre = parse('$.films[*].genres')
        film_genre = jsonpath_genre.find(json_data)
        jsonpath_rating = parse('$.films[*].rating')
        film_rating = jsonpath_rating.find(json_data)
        jsonpath_poster = parse('$.films[*].posterUrl')
        film_poster = jsonpath_poster.find(json_data)
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
            cinema: Cinema = Cinema(film_id=film_id,
                                    name=name,
                                    year=year,
                                    length=length,
                                    country=country,
                                    genre=genre,
                                    rating=rating,
                                    poster=poster)
            list_movie.append(cinema)
        obj = Billboard(list_movie)
        return obj

    def send_spin_offs(self, movie_name: str) -> list[Film]:
        self.set_id_kino_poisk(movie_name)
        url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/{int(self.id_kino_poisk)}/sequels_and_prequels'
        res = requests.get(url=url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_film_id = parse('$..[filmId]')
        film_id = jsonpath_film_id.find(json_data)
        jsonpath_name = parse('$..[nameRu]')
        film_name = jsonpath_name.find(json_data)
        list_film_id = list(map(lambda x: x.value, film_id))
        list_film_name = list(map(lambda x: x.value, film_name))
        list_film: list[Film] = []
        for film_id, name in zip(list_film_id, list_film_name):
            film: Film = Film(film_name=name, film_id=film_id, description=self.give_data_about_film(film_id))
            list_film.append(film)
        return list_film
