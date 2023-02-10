import re

import requests
from bs4 import BeautifulSoup
from kinopoisk.movie import Movie

from webServase.KinopoiskAPIDev import KinopoiskAPIDev


class Searcher(object):
    __URL: str = 'https://www.kinopoisk.ru/index.php'
    __headers: dict = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

    def __give_html(self, query: str) -> tuple:
        params = {'kp_query': query}
        session = requests.session()
        response = session.get(url=self.__URL,
                               headers=self.__headers,
                               params=params,
                               allow_redirects=False)
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'captcha' in content:
                return requests.codes.ok, None
            else:
                return requests.codes.ok, content
        elif response.status_code == 302:
            return requests.codes.found, None

    def parse(self, query: str) -> list[dict[str, str]]:
        status_code, html = self.__give_html(query)
        list_film_id = []
        if status_code == 200:
            if html is None:
                movies = Movie.objects.search(query)[:5]
                for movie in movies:
                    movie_name = movie.name
                    if movie_name.casefold() == query.casefold():
                        my_dict = {'film_name': movie_name, 'film_id': movie.id}
                        list_film_id.append(my_dict)
            else:
                soup = BeautifulSoup(html, "lxml")
                tmp_href = ''
                for a in soup.find_all('a', attrs={'data-id': True, 'data-type': lambda x: x != 'person'}):
                    href = a.get('href')
                    if href.endswith('sr/1/') and a.text != '' and href != tmp_href:
                        film_name_no_special_characters = a.text

                        if '\xa0' in film_name_no_special_characters:
                            film_name_no_special_characters = re.sub('\xa0', ' ', a.text).strip()
                        if '–' in film_name_no_special_characters:
                            film_name_no_special_characters = re.sub('[–—]', '-', a.text).strip()

                        film_name = ' '.join(word for word in film_name_no_special_characters.split() if
                                             not word.startswith('(') and not word.endswith(')'))
                        if film_name.casefold() == query.casefold():
                            my_dict = {'film_name': film_name, 'film_id': a.get('data-id')}
                            list_film_id.append(my_dict)
                            tmp_href = href
        elif status_code == 302:
            list_film_id.append(KinopoiskAPIDev().get_film_title_and_id(query))
        return list_film_id
