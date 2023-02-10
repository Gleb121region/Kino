import re

from Data import Cinema
from Text.messagesPattern import stencil
from Text.regexText import *
from converterStringDataToMinet import hms_to_s


class Billboard(object):
    def __init__(self,
                 list_film: list[Cinema]):
        self.list_film = list_film

    def send_message_in_tg(self) -> list[dict]:
        list_film_about: list[dict] = []
        for cinemas in self.list_film:
            genre_str: str = ''
            for genre in cinemas.genre:
                if isinstance(genre, dict):
                    genre_str += genre.get('genre') + ' '
                if isinstance(genre, str):
                    genre_str += genre + ' '

            movie_title = re.search(regex_for_title, str(cinemas.name)).group(0)
            movie_poster_url = re.search(regex_for_url, cinemas.poster).group(0)
            movie_year = re.search(regex_for_digit, str(cinemas.year)).group(0)
            movie_length = hms_to_s(re.search(regex_for_digit, str(cinemas.length)).group(0))
            movie_country = ' '.join(map(str, re.findall(regex_for_word_and_space, str(cinemas.country))[0:]))
            movie_genre = ' '.join(map(str, re.findall(regex_for_word_and_space, str(genre_str))[0:]))
            movie_rating = re.search(regex_for_rating, str(cinemas.rating)).group(0)

            text = stencil(movie_title, movie_poster_url, movie_year, movie_length, movie_country, movie_genre,
                           movie_rating)

            movie_id = re.search(regex_for_digit, str(cinemas.film_id)).group(0)
            from webServase.VideoCDN import VideoCDN
            movie_video_url = VideoCDN().get_film_link_by_kinoP_id(int(movie_id))
            if isinstance(movie_video_url, str):
                MyDictionary = {movie_video_url: text}
                list_film_about.append(MyDictionary)
        return list_film_about

