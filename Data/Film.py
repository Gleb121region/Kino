class Film(object):

    def __init__(self, film_name: str, film_id: int, film_poster: str):
        self.film_name = film_name,
        self.film_id = film_id,
        self.film_poster = film_poster

    def send_similar_films(self) -> str:
        from VX import VX
        film = f'<b>{self.film_name}</b>\n' \
               f'<b>Ссылка для просмотра:</b> {VX().get_film_by_kinopoisk_id(self.film_id)}\n' \
               f'Постер: {self.film_poster}\n' \
            .replace("\'", '') \
            .replace(')', '').replace('(', '') \
            .replace(',', '')
        return film
