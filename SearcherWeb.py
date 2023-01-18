import re

import requests
from bs4 import BeautifulSoup


class SearcherWeb(object):
    headers: dict[str, str] = {
        'User-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    expected_site: str = 'www.kinopoisk.ru'
    URL: str = 'https://www.google.com/search'

    def search_google_and_find_kino_poisk_id(self, film_name: str) -> list[dict[str, str]]:
        params = {
            'q': f'{film_name} url: {self.expected_site}',
            'gl': 'us',
            'hl': 'en'
        }
        response = requests.get(self.URL, headers=self.headers, params=params)
        soup = BeautifulSoup(response.text, 'lxml')
        list_film_id = []
        for result in soup.select('.tF2Cxc'):
            title = result.select_one('.DKV0Md').text
            link = result.select_one('.yuRUbf a')['href']
            if 'film' or 'series' in link:
                my_dict = {'film_name': title, 'film_id': re.search("\d+", link).group()}
                list_film_id.append(my_dict)
        return list_film_id
