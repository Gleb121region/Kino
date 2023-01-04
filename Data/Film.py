class Film(object):

    def __init__(self, film_name, film_id, film_poster):
        self.film_name = film_name,
        self.film_id = film_id,
        self.film_poster = film_poster

    def send_message_in_tg(self) -> str:
        from VX import VX
        film = f'О кинопроизведении {self.film_name}\n'
        f'Ссылка на фильм: {VX().get_film_by_kinopoisk_id(self.film_id)}\n'
        f'Постер: {self.film_poster}\n'
        return film
