from peewee import *

db = SqliteDatabase('telebot.db')


class Movie(Model):
    movie_id = PrimaryKeyField(unique=True, null=False)
    movie_title = TextField()
    movie_poster_url = TextField(unique=True)
    movie_year = DateField()
    movie_country = TextField
    movie_genre = TextField()
    movie_rating = FloatField()

    @staticmethod
    def list():
        query = Movie.select()
        for row in query:
            print(row.movie_id, row.movie_title, row.movie_poster_url, row.movie_year, row.movie_country,
                  row.movie_genre,
                  row.movie_rating)

    class Meta:
        database = db
        order_by = 'movie_id'
        db_table = 'movies'


class User(Model):
    user_id = IntegerField(unique=True, null=False)
    username = CharField()
    first_name = CharField()
    last_name = CharField(null=True)

    @staticmethod
    def list():
        query = User.select()
        for row in query:
            print(row.user_id, row.username, row.first_name, row.last_name)

    class Meta:
        database = db
        order_by = 'user_id'
        db_table = 'users'


class User2Movie(Model):
    user_movie_id = PrimaryKeyField(unique=True, null=False)
    user_id = ForeignKeyField(User, to_field='user_id')
    movie_id = ForeignKeyField(Movie, to_field='movie_id')

    @staticmethod
    def list():
        query = User2Movie.select()
        for row in query:
            print(row.user_movie_id, row.user_id, row.movie_id)

    class Meta:
        database = db
        order_by = 'id'
        db_table = 'user2movies'
