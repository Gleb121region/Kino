from Model import models
from Text import messagesPattern
from VX import VX


def get_movie_id_by_movie_video_url(movie_video_url: str) -> int:
    with models.db:
        return models.Movie.select().where(models.Movie.movie_video_url == movie_video_url).get().movie_id


def get_movie_by_film_title(movie_title: str) -> list[dict[str, str]] | None:
    list_dict: list[dict[str, str]] = []
    with models.db:
        query = models.Movie.select().where(models.Movie.movie_title == movie_title.casefold())
        movie_selected = query.dicts().execute()
        if len(movie_selected) > 0:
            for movie in movie_selected:
                movie_id = movie.get('movie_id')
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

                movie_video_url = VX().get_film_link_by_kinopoisk_id(int(movie_id))
                my_Dict = {movie_video_url: text}
                list_dict.append(my_Dict)
        else:
            return None
    return list_dict
