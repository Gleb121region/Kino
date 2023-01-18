import re

import requests
from bs4 import BeautifulSoup


class Searcher(object):
    URL: str = 'https://www.kinopoisk.ru/index.php'

    def give_html(self, query: str) -> str:
        params = {'kp_query': query}
        session = requests.session()
        response = session.get(url=self.URL, params=params)
        if response:
            content = response.content.decode('utf-8')
            if 'captcha' in content:
                raise ValueError('Kino poisk block this IP. Too many requests')
            return content

    def parse(self, query: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(self.give_html(query))
        list_film_id = []
        all_film = soup.find_all(href=re.compile('/film/'))
        for a in all_film:
            film_name = a.text.replace('\xa0', ' ').replace(' (сериал)'.casefold(), '').replace(
                '(мини-сериал)'.casefold(), '').strip()
            my_dict = {'film_name': film_name, 'film_id': a.get('data-id')}
            list_film_id.append(my_dict)
        return list_film_id
