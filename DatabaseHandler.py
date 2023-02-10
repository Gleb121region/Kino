import re
import traceback

from Model import models
from Text import messagesPattern
from Text.regexText import regex_for_county, regex_for_genre
from webServase.VideoCDN import VideoCDN


def __get_movie_by_X(query):
    list_dict: list[dict[str, str]] = []
    with models.db:
        movie_selected = query.dicts().execute()
        if len(movie_selected) > 0:
            for movie in movie_selected:
                movie_id = movie.get('movie_id')
                movie_title = movie.get('movie_title')
                movie_len = movie.get('movie_len')
                movie_year = movie.get('movie_year')
                movie_genre = movie.get('movie_genre')
                movie_country = movie.get('movie_country')
                movie_rating = movie.get('movie_rating')
                movie_poster_url = movie.get('movie_poster_url')

                text = messagesPattern.stencil(
                    movie_title=movie_title,
                    movie_length=movie_len,
                    movie_year=movie_year,
                    movie_genre=movie_genre,
                    movie_country=movie_country,
                    movie_rating=movie_rating,
                    movie_poster_url=movie_poster_url)

                movie_video_url = VideoCDN().get_film_link_by_kinoP_id(int(movie_id))
                my_Dict = {movie_video_url: text}
                list_dict.append(my_Dict)
        else:
            return None
    return list_dict


def __check_favourite_movie_for_user(user_id, movie_id):
    with models.db:
        return len(models.User2Movie.select().where(
            models.User2Movie.user_id == user_id and models.User2Movie.movie_id == movie_id).dicts().execute())


def __check_movie_by_id(movie_id):
    with models.db:
        return len(models.Movie.select().where(models.Movie.movie_id == movie_id).dicts().execute())


def __check_movie_by_video_url(movie_video_url):
    with models.db:
        return len(models.Movie.select().where(models.Movie.movie_video_url == movie_video_url).dicts().execute())


def __check_user(user_id):
    with models.db:
        return len(models.User.select().where(models.User.user_id == user_id).dicts().execute())


def get_movie_id_by_movie_video_url(movie_video_url: str) -> int:
    with models.db:
        if __check_movie_by_video_url(movie_video_url) != 0:
            return models.Movie.select().where(models.Movie.movie_video_url == movie_video_url).get().movie_id


def get_movie_by_movie_id(movie_id: int):
    with models.db:
        query = models.Movie.select().where(models.Movie.movie_id == movie_id)
    return __get_movie_by_X(query)


def get_list_favorite_movies_by_user_id(user_id: int) -> list:
    with models.db:
        query = models.Movie.select().join(models.User2Movie).where(models.User2Movie.user_id == user_id)
        return list(map(lambda x: x, query))


def get_movie_by_film_title(movie_title: str) -> list[dict[str, str]] | None:
    with models.db:
        query = models.Movie.select().where(models.Movie.movie_title == movie_title)
    return __get_movie_by_X(query)


def add_favourite_movie(user_id, movie_id):
    if __check_favourite_movie_for_user(user_id, movie_id) == 0:
        with models.db:
            models.User2Movie.create(
                user_id=user_id,
                movie_id=movie_id
            )


def add_user(user_id, username, full_name):
    with models.db:
        if __check_user(user_id) == 0:
            models.User.create(user_id=user_id, username=username, full_name=full_name)


def add_movie(film_id, name, year, length, country, genre, rating, poster):
    with models.db:
        try:
            from webServase.VideoCDN import VideoCDN
            if __check_movie_by_id(film_id) == 0:
                country = re.sub(regex_for_county, '', str(country))
                genre = re.sub(regex_for_genre, '', str(genre))
                movie_video_url = VideoCDN().get_film_link_by_kinoP_id(film_id)
                if movie_video_url is not None:
                    models.Movie.create(movie_id=int(film_id),
                                        movie_title=str(name).lower().capitalize(),
                                        movie_rating=rating,
                                        movie_genre=genre,
                                        movie_poster_url=poster,
                                        movie_len=length,
                                        movie_year=year,
                                        movie_country=country,
                                        movie_video_url=movie_video_url
                                        )
        except Exception as e:
            print(traceback.format_exc())
