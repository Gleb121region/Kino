from Data import Description


class Film(object):

    def __init__(self, film_name: str, film_id: int, description: Description):
        self.film_name: str = film_name
        self.film_id: int = film_id
        self.description = description

    def send_info_about_film(self) -> dict:
        text = f'<b>{self.film_name}</b>\n' \
               f'Постер: {self.description.poster}\n' \
               f'Год производства: {self.description.year}\n' \
               f'Длительность: {self.description.duration}\n' \
               f'Страна: {self.description.countries}\n' \
               f'Жанр: {self.description.genres}\n' \
               f'Рейтинг по отзывам: {self.description.rating}'.replace("\'", '') \
            .replace(')', '').replace('(', '') \
            .replace(',', '').replace('[', '').replace(']', '')
        film_id = self.film_id
        my_dict = {film_id: text}
        return my_dict
