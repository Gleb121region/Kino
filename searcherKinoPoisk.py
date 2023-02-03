import requests
from bs4 import BeautifulSoup
from kinopoisk.movie import Movie


class Searcher(object):
    __URL: str = 'https://www.kinopoisk.ru/index.php'

    def __give_html(self, query: str) -> str | None:
        params = {'kp_query': query}
        session = requests.session()
        response = session.get(url=self.__URL, params=params)
        if response.ok:
            content = response.content.decode('utf-8')
            if 'captcha' in content:
                return None
            return content

    def parse(self, query: str) -> list[dict[str, str]]:
        html = self.__give_html(query)
        if html is None:
            list_film_id = []
            for i in range(5):
                movie = Movie.objects.search(query)[i]
                movie_id = movie.id
                movie_name = movie.name
                if movie_name.casefold() == query.casefold():
                    my_dict = {'film_name': movie_name, 'film_id': movie_id}
                    list_film_id.append(my_dict)
            return list_film_id
        soup = BeautifulSoup(html, "lxml")
        list_film_id = []
        tmp_href = ''
        for a in (a_data_id for a_data_id in soup.select('a[data-id]') if
                  a_data_id.get('data-id') is not None and a_data_id.get('data-type') != 'person'):
            href = a.get('href')
            if href.endswith('sr/1/') and a.text != '':
                if href != tmp_href:
                    print(a.text)
                    film_name = a.text.replace('\xa0', ' ').replace(' (сериал)'.casefold(), '').replace(
                        '(мини-сериал)'.casefold(), '').strip()
                    if film_name.casefold() == query.casefold():
                        my_dict = {'film_name': film_name, 'film_id': a.get('data-id')}
                        list_film_id.append(my_dict)
                        tmp_href = href
        return list_film_id
