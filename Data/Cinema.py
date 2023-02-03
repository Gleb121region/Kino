class Cinema(object):
    def __init__(self, film_id: int,
                 name,
                 year,
                 length,
                 country: list[dict[str]],
                 genre: list[dict[str]],
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
