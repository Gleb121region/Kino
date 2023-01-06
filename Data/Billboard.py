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

    def send_message_in_tg(self) -> list[dict]:
        list_film_about: list[dict] = []
        for cinemas in self.list_film:
            county_str: str = ''
            for county in cinemas.country:
                county_str += county.get('country') + ' '
            genre_str: str = ''
            for genre in cinemas.genre:
                genre_str += genre.get('genre') + ' '
            text = f'<b>{cinemas.name}</b>\n' \
                   f'Постер: {cinemas.poster}\n' \
                   f'Год производства: {cinemas.year}\n' \
                   f'Длительность: {cinemas.length}\n' \
                   f'Страна: {county_str}\n' \
                   f'Жанр: {genre_str}\n' \
                   f'Рейтинг по отзывам: {cinemas.rating}' \
                .replace("(", '').replace(")", '') \
                .replace(",", '').replace("'", '')
            MyDictionary = {cinemas.film_id: text}
            list_film_about.append(MyDictionary)
        return list_film_about

    def send_message_in_tg_minimalistic(self) -> str:
        text_message = ''
        for cinemas in self.list_film:
            from VX import VX
            film_id_str = str(cinemas.film_id).replace('(', '').replace(')', '').replace(',', '')
            film_link = VX().get_film_link_by_kinopoisk_id(int(film_id_str))
            text = f'<b>{cinemas.name}</b>\n' \
                   f'Постер: {cinemas.poster}\n' \
                   f'Ссылка для просмотра: {film_link}' \
                .replace("(", '').replace(")", '') \
                .replace(",", '').replace("'", '')
            print(text)
            text_message += text
        return text_message
