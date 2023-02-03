import re

from Data import Description
from Text.messagesPattern import stencil


class Film(object):

    def __init__(self, film_name: str, film_id: int, description: Description):
        self.film_name: str = film_name
        self.film_id: int = film_id
        self.description = description

    def send_info_about_film(self) -> dict:
        movie_title = re.search(r'[\w\s-]+', str(self.film_name)).group(0)
        movie_poster_url = re.search(r'[\w://.]+', str(self.description.poster)).group(0)
        movie_year = re.search(r'\d+', str(self.description.year)).group(0)
        movie_length = re.search(r'\d+', str(self.description.length)).group(0)
        movie_country = re.search(r'[\w\s]+', str(self.description.country)).group(0)
        movie_genre = re.search(r'[\w\s]+', str(self.description.genre)).group(0)
        movie_rating = re.search(r'\d+\.\d+', str(self.description.rating)).group(0)

        text = stencil(movie_title, movie_poster_url, movie_year, movie_length, movie_country, movie_genre, movie_rating)

        from VX import VX
        movie_video_url = VX().get_film_link_by_kinoP_id(int(self.film_id))
        my_Dict = {movie_video_url: text}
        return my_Dict
