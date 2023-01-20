import requests
from bs4 import BeautifulSoup

from SearcherWeb import SearcherWeb


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
        tmp_href = ''
        for a in (a_data_id for a_data_id in soup.select('a[data-id]') if
                  a_data_id.get('data-id') is not None and a_data_id.get('data-type') != 'person'):
            href = a.get('href')
            if href.endswith('sr/1/') and a.text != '':
                if href != tmp_href:
                    film_name = a.text.replace('\xa0', ' ').replace(' (сериал)'.casefold(), '').replace(
                        '(мини-сериал)'.casefold(), '').strip()
                    my_dict = {'film_name': film_name, 'film_id': a.get('data-id')}
                    list_film_id.append(my_dict)
                    tmp_href = href
        return list_film_id
