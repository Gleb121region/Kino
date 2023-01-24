import re

from converterStringDataToMinet import hms_to_s


def stencil(movie_title, movie_poster_url, movie_year, movie_length, movie_country, movie_genre, movie_rating) -> str:
    if ':' in movie_length:
        movie_length = hms_to_s(movie_length)

    if ":" in movie_country:
        movie_country = ' '.join(map(str, re.findall(r'\w+', str(movie_country))[1:]))

    if ":" in movie_genre:
        movie_genre = ' '.join(map(str, re.findall(r'\w+', str(movie_genre))[1::2]))

    text = (f'<b> {movie_title}</b>\n'
            f'Постер: {movie_poster_url}\n'
            f'Год производства: {movie_year}\n'
            f'Длительность: {movie_length} мин\n'
            f'Страна: {movie_country}\n'
            f'Жанр: {movie_genre}\n'
            f'Рейтинг по отзывам: {movie_rating}')
    return text
