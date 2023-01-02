class Cinema(object):
    def __init__(self, film_id,
                 name,
                 year,
                 length,
                 country,
                 genre,
                 rating,
                 poster):
        self.film_id = film_id,
        self.name = name,
        self.year = year,
        self.length = length,
        self.country = country,
        self.genre = genre
        self.rating = rating,
        self.poster = poster


class Billboard(object):
    def __init__(self,
                 list_film: list[Cinema]):
        self.list_film = list_film

    def do_html_code(self) -> str:
        return ""
