from telebot.asyncio_handler_backends import State, StatesGroup


class Movie(StatesGroup):
    name = State()


class Keyword(StatesGroup):
    word = State()


class Cinematography(StatesGroup):
    name = State()
