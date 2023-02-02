from Data import Description


class Film(object):

    def __init__(self, film_name: str, film_id: int, description: Description):
        self.film_name: str = film_name
        self.film_id: int = film_id
        self.description = description
    # todo: переписать без replace
    def send_info_about_film(self) -> dict:
        text = (f'<b>{self.film_name}</b>\n'
                f'Постер: {self.description.poster}\n'
                f'Год производства: {self.description.year}\n'
                f'Длительность: {self.description.length}\n'
                f'Страна: {self.description.country}\n'
                f'Жанр: {self.description.genre}\n'
                f'Рейтинг по отзывам: {self.description.rating}'.replace("\'", '')
                .replace(')', '').replace('(', '')
                .replace(',', '').replace('[', '').replace(']', ''))
        from VX import VX
        movie_video_url = VX().get_film_link_by_kinopoisk_id(int(self.film_id))
        my_Dict = {movie_video_url: text}
        return my_Dict
