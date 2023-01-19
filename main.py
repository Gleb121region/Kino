import asyncio
import os
import traceback

from telebot import asyncio_filters
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from KinoPoisk import KinoPoisk
from VX import VX

bot = AsyncTeleBot(os.getenv('telegram_token'), state_storage=StateMemoryStorage())


class Movie(StatesGroup):
    name = State()


class Keyword(StatesGroup):
    word = State()

class Cinematography(StatesGroup):
    name = State()

def webpage_and_favorites_list_add_handler(film_id: str):
    markup = InlineKeyboardMarkup()
    film_id = film_id.replace(',', '').replace('(', '').replace(')', '')
    film_link = VX().get_film_link_by_kinopoisk_id(int(film_id))
    if film_link is None:
        markup.add(InlineKeyboardButton('Добавить в избранное', callback_data=film_id))
    else:
        markup.add(InlineKeyboardButton('Добавить в избранное', callback_data=film_id),
                   InlineKeyboardButton('Ссылка для просмотра', url=film_link))
    return markup


def next_button_handler(page_number: str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Следующий', callback_data=page_number))
    return markup


# команды без state
########################################################################################################################
@bot.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    first_name: str = message.from_user.first_name
    last_name: str = message.from_user.last_name
    message_for_user: str
    if last_name is None or last_name == 'None'.casefold():
        message_for_user = f'<b>Привет, {first_name} Этот бот показывает фильмы по запросу попробуй</b>'
    else:
        message_for_user = f'<b>Привет, {first_name} {last_name} Этот бот показывает фильмы по запросу попробуй</b>'
    await bot.send_message(message.chat.id,
                           message_for_user,
                           parse_mode='html')


# команда для отправления топа фильмов
# надо сделать свой json файл, который буду обновлять раз в неделю
@bot.message_handler(commands=['top'])
async def send_top_film(message: types.Message):
    page_number = 1
    billboard = KinoPoisk().give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await bot.send_message(message.chat.id,
                                   value,
                                   parse_mode='html',
                                   disable_notification=True,
                                   reply_markup=webpage_and_favorites_list_add_handler(str(key)))

    await  bot.send_message(message.chat.id,
                            'Предлагаем вашему вниманию следующие кинопроизведения',
                            disable_notification=True,
                            reply_markup=next_button_handler(str(page_number + 1)))


# команды со state
########################################################################################################################
# команда для отправления аналогов фильма
@bot.message_handler(commands=['recommendation'])
async def handler_send_recommendation(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Movie.name, message.chat.id)
    await bot.send_message(message.chat.id, 'Введите название фильма', reply_to_message_id=message.message_id,
                           reply_markup=force_reply)


@bot.message_handler(state=Movie.name)
async def send_recommendation(message: types.Message):
    try:
        film_name = message.text
        message_for_user = 'Если вам понравился этот фильм Бот отправляет похожие фильмы'.format(film_name)
        await bot.send_message(message.chat.id, message_for_user)
        list_similar_films = KinoPoisk().give_recommendations(str(film_name))
        for film in list_similar_films:
            for key, value in film.send_info_about_film().items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=webpage_and_favorites_list_add_handler(str(key)))
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        print(traceback.format_exc())


# команда поиск фильма по ключевому слову (не фраза)
@bot.message_handler(commands=['search'])
async def handler_send_film_by_keyword(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Keyword.word, message.chat.id)
    await bot.send_message(message.chat.id, 'Введите ключевые слова', reply_to_message_id=message.message_id,
                           reply_markup=force_reply)


@bot.message_handler(state=Keyword.word)
async def send_film_by_keyword(message: types.Message):
    page_number = 1
    try:
        keyword = message.text
        billboard = KinoPoisk().give_films_by_keyword(keyword=str(keyword), page_number=page_number)
        for film_info in billboard.send_message_in_tg():
            for key, value in film_info.items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=webpage_and_favorites_list_add_handler(str(key)))
        await bot.delete_state(message.from_user.id, message.chat.id)
    except Exception as e:
        print(traceback.format_exc())


#  команда поиск фильмов (предысторий и сиквелов)
@bot.message_handler(commands=['story'])
async def handler_send_background(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Keyword.word, message.chat.id)
    await bot.send_message(message.chat.id, 'Введите название фильма', reply_to_message_id=message.message_id,
                           reply_markup=force_reply)

@bot.message_handler(state=Cinematography.name)
async def send_background(message: types.Message):
    film_name = message.text
    try:
        for film in KinoPoisk().send_spin_offs(film_name):
            for key, value in film.send_info_about_film().items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    except Exception as e:
        print()


#  кнопочки
@bot.callback_query_handler(func=lambda call: call.data.isdigit() == True)
async def callback_query(call):
    kino = KinoPoisk()
    page_number = int(call.data)
    billboard = kino.give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await bot.send_message(call.message.chat.id,
                                   value,
                                   parse_mode='html',
                                   disable_notification=True,
                                   reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    await  bot.send_message(call.message.chat.id,
                            'Предлагаем вашему вниманию следующие кинопроизведения',
                            disable_notification=True,
                            reply_markup=next_button_handler(str(page_number + 1)))


#  поиск
@bot.message_handler(func=lambda message: True)
async def send_film_by_film_name(message):
    try:
        links = VX().get_film_link_by_name(message.text)
        for link in links:
            for key, value in link.items():
                await bot.send_message(message.chat.id, value, parse_mode='html',
                                       reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    except Exception as e:
        print(traceback.format_exc())


if __name__ == '__main__':
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.add_custom_filter(asyncio_filters.IsDigitFilter())

    asyncio.run(bot.polling(none_stop=True))


