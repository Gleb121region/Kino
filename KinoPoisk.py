import os

import requests
import json

from jsonpath_ng import parse
from kinopoisk.movie import Movie

from Data.Billboard import Billboard
from Data.Billboard import Cinema
from Data.Description import Description
from Data.Film import Film
from Data.Thriller import Thriller


class KinoPoisk(object):
    URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
    API_TOKEN = os.getenv('kino_poisk_token')
    headers = {'X-API-KEY': API_TOKEN, 'Content-Type': 'application/json'}
    id_kino_poisk = ''

    def get_id_kino_poisk(self, name: str) -> str:
        return Movie.objects.search(name)[0].id

    def set_id_kino_poisk(self, name: str):
        mov = Movie.objects.search(name)
        self.id_kino_poisk = str(mov[0].id)

    def give_recommendations(self, name: str):
        self.set_id_kino_poisk(name)
        url: str = self.URL + self.id_kino_poisk + '/similars'
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_name = parse('$.items[*].nameRu')
        names = jsonpath_name.find(json_data)
        jsonpath_film_id = parse('$.items[*].filmId')
        ids = jsonpath_film_id.find(json_data)
        jsonpath_poster = parse("$.items[*].posterUrl")
        posters = jsonpath_poster.find(json_data)
        jsonpath_size = parse("$.total")
        #  todo: чуть позже посмотреть нужен ли вообще size…
        size = jsonpath_size.find(json_data)
        try_size = size[0].value
        list_films = []
        for i in range(try_size):
            name = str(names[i].value)
            id_string = str(ids[i].value)
            poster = str(posters[i].value)
            film_info = Film(film_name=name, film_id=id_string, film_poster=poster)
            list_films.append(film_info)
        return list_films

    def give_data_about_film(self, name: str) -> Description:
        self.set_id_kino_poisk(name)
        url = self.URL + self.id_kino_poisk
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_poster = parse("$.posterUrl")
        posters = jsonpath_poster.find(json_data)
        poster = posters[0].value
        jsonpath_rating = parse("$.ratingKinopoisk")
        ratings = jsonpath_rating.find(json_data)
        rating = ratings[0].value
        jsonpath_year = parse("$.year")
        years = jsonpath_year.find(json_data)
        year = years[0].value
        jsonpath_description = parse("$.description")
        descriptions = jsonpath_description.find(json_data)
        description_data = descriptions[0].value
        jsonpath_type = parse("$.type")
        types = jsonpath_type.find(json_data)
        data_type = types[0].value

        jsonpath_county = parse("$.countries[*].country")
        counties = jsonpath_county.find(json_data)
        list_counties = list(map(lambda x: x.value, counties))

        jsonpath_genres = parse("$.genres[*].genre")
        genres = jsonpath_genres.find(json_data)
        list_genres = list(map(lambda x: x.value, genres))

        jsonpath_start_year = parse("$.startYear")
        start_years = jsonpath_start_year.find(json_data)
        start_year = start_years[0].value

        jsonpath_end_year = parse("$.endYear")
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
                           end_year=end_year)
        return data

    def give_thriller(self, name: str) -> Thriller:
        self.set_id_kino_poisk(name)
        url = self.URL + self.id_kino_poisk + '/videos'
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)
        jsonpath_url = parse("$.items[*].url")
        jsonpath_name = parse("$.items[*].name")
        urls = jsonpath_url.find(json_data)
        names = jsonpath_name.find(json_data)
        list_url = list(map(lambda x: x.value, urls))
        list_name = list(map(lambda x: x.value, names))
        data = Thriller(names=list_name, urls=list_url)
        return data

    def give_top_films(self, pageNum: str) -> Billboard:
        url = self.URL + f'top?page={pageNum}'
        res = requests.get(url, headers=self.headers)
        json_string = res.text
        json_data = json.loads(json_string)

        jsonpath_film_id = parse("$.films[*].filmId")
        film_id = jsonpath_film_id.find(json_data)
        jsonpath_name = parse("$.films[*].nameRu")
        film_name = jsonpath_name.find(json_data)
        jsonpath_year = parse("$.films[*].year")
        film_year = jsonpath_year.find(json_data)
        jsonpath_film_len = parse("$.films[*].filmLength")
        film_len = jsonpath_film_len.find(json_data)
        jsonpath_country = parse("$.films[*].countries[*]")
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
        for i in list_movie:
            print(i.film_id)
        obj = Billboard(list_movie)
        return obj
