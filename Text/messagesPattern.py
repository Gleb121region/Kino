import re


def stencil(movie_title, movie_poster_url, movie_year, movie_length, movie_country, movie_genre, movie_rating) -> str:
    if isinstance(movie_country, str):
        movie_country = movie_country.replace('country', '')

    if isinstance(movie_genre, str):
        movie_genre = ' '.join(map(str, re.findall(r'\w+', str(movie_genre))[1::2]))

    text = (f'<b> {movie_title}</b>\n'
            f'Постер: {movie_poster_url}\n'
            f'Год производства: {movie_year}\n'
            f'Длительность: {movie_length} мин\n'
            f'Страна: {movie_country}\n'
            f'Жанр: {movie_genre}\n'
            f'Рейтинг по отзывам: {movie_rating}')
    return text
