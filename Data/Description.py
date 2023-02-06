class Description(object):
    def __init__(self, poster: str, rating: float | int, year: int, country: str, genre: str, length: int):
        self.poster = poster,
        self.rating = rating,
        self.year = year,
        self.country = country,
        self.genre = genre,
        self.length = length
