import re

import requests
from bs4 import BeautifulSoup


class SearcherWeb(object):
    __headers: dict[str, str] = {
        'User-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    __expected_site: str = 'www.kinopoisk.ru'
    __URL: str = 'https://www.google.com/search'

    def search_google_and_find_kino_poisk_id(self, film_name: str) -> list[dict[str, str]]:
        params = {
            'q': f'{film_name} url: {self.__expected_site}',
            'gl': 'us',
            'hl': 'en'
        }
        response = requests.get(self.__URL, headers=self.__headers, params=params)
        soup = BeautifulSoup(response.text, 'lxml')
        list_film_id = []
        for result in soup.select('.tF2Cxc'):
            title = result.select_one('.DKV0Md').text
            link = result.select_one('.yuRUbf a')['href']
            if 'film' or 'series' in link:
                print(title)
                print(link)
                try:
                    film_id = re.search("\d+", link).group()
                    my_dict = {'film_name': title, 'film_id': film_id}
                    list_film_id.append(my_dict)
                except AttributeError:
                    pass
        return list_film_id
