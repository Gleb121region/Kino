import requests
from bs4 import BeautifulSoup


class Searcher(object):
    proxy = 'http://proxy.server:3128'
    URL = 'https://www.kinopoisk.ru/index.php'

    def give_html(self, query: str):
        params = {'kp_query': query}
        response = requests.get(url=self.URL,
                                params=params,
                                proxies=self.proxy)
        if response:
            content = response.content.decode('utf-8')
            if 'captcha' in content:
                raise ValueError('Kino poisk block this IP. Too many requests')
            return content

    def parse(self, query: str) -> list[dict]:
        soup = BeautifulSoup(self.give_html(query))
        list_film_id = []
        for a in soup.select('a[data-id]'):
            if a.get('href').endswith('sr/1/') and a.text != '':
                film_name = a.text.replace('\xa0', ' ').replace(' (сериал)'.casefold(), '').replace(
                    '(мини-сериал)'.casefold(), '').strip()

                my_dict = {'film_name': film_name, 'film_id': a.get('data-id')}
                list_film_id.append(my_dict)
        return list_film_id
