import json
import os

import requests
from jsonpath_ng import parse
from spellchecker import SpellChecker

google_api_key = os.getenv('google_api_token')
cx = os.getenv('cx')

# проверка есть ли такой фильм в "Кинопоиске" вообще
def check_the_correct_spelling_on_the_internet(text: str) -> str | None:
    response = requests.get(f'https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={cx}&q={text}')
    if response.ok:
        json_data = json.loads(response.text)
        jsonpath_title = parse('$.items[0].title')
        film_title = jsonpath_title.find(json_data)
        title: str = film_title[0].value
        sep = '('
        sep2 = '—'
        if sep in title:
            normal = title.split(sep, 1)[0].strip()
            return normal
        if sep2 in title:
            normal = title.split(sep2, 1)[0].strip()
            return normal
    else:
        return None


#  проверка грамматики
def check_text_for_correct_spelling(text: str) -> str | None:
    txt1 = text.split()
    spell = SpellChecker(language='ru')
    misspelled = spell.unknown(txt1)
    for word in misspelled:
        if len(word) == 1:
            pass
        else:
            right_writing = spell.correction(word)
            if right_writing is not None:
                normal = text.replace(word, right_writing)
                return normal
            else:
                answer = check_the_correct_spelling_on_the_internet(text)
                return answer
    return text
