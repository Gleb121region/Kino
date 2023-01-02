import urllib
import requests


class ChangeLink(object):
    API_TOKEN = '98eb92c64a954b32ef7b8a67ff077cd42c2b9'
    URL = ''

    def __init__(self, URL: str):
        self.URL = URL

    def shorter_link(self, link_name):
        base_url = 'https://cutt.ly/api/api.php'
        params = {'key': self.API_TOKEN, 'short': self.URL, 'name': link_name}
        res = requests.get(base_url, params=params)
        print(res.text)


