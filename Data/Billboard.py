class Cinema(object):
    def __init__(self, film_id: int,
                 name,
                 year,
                 length,
                 country: dict[str],
                 genre: list[dict[str]],
                 rating,
                 poster):
        self.film_id = film_id,
        self.name = name,
        self.year = year,
        self.length = length,
        self.country = country,
        self.genre = genre
        self.rating = rating,
        self.poster = poster


class Billboard(object):
    def __init__(self,
                 list_film: list[Cinema]):
        self.list_film = list_film

    def send_message_in_tg(self) -> list[str]:
        list_film_about: list[str] = []
        for cinemas in self.list_film:
            county_str: str = ''
            for county in cinemas.country:
                county_str += county.get('country') + ' '
            genre_str: str = ''
            for genre in cinemas.genre:
                genre_str += genre.get('genre') + ' '
            from VX import VX
            list_film_about.append(f'О кинопроизведении {cinemas.name}\n'
                                   f'Ссылка на фильм: {VX().get_film_by_kinopoisk_id(cinemas.film_id)}\n'
                                   f'Постер: {cinemas.poster}\n'
                                   f'Год производства: {cinemas.year}\n'
                                   f'Длительность: {cinemas.length}\n'
                                   f'Страна: {county_str}\n'
                                   f'Жанр: {genre_str}\n'
                                   f'Рейтинг по отзывам: {cinemas.rating}'
                                   .replace("',)", '')
                                   .replace("('", '')
                                   )
        return list_film_about
