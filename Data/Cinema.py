class Cinema(object):
    def __init__(self, film_id: int, name: str, year: int, length: int, country: list[dict[str]],
                 genre: list[dict[str]], rating: float | int, poster: str):
        self.film_id = film_id
        self.name = name
        self.year = year
        self.length = length
        self.country = country
        self.genre = genre
        self.rating = rating
        self.poster = poster
