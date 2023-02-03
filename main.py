import asyncio
import os
import traceback

from loguru import logger
from telebot import asyncio_filters
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from DatabaseHandler import *
from KinoPoisk import KinoPoisk
from Model import models
from States.states import Movie, Keyword, Cinematography
from Text.messages import *

bot = AsyncTeleBot(os.getenv('telegram_token'), state_storage=StateMemoryStorage())


# кнопки для пользователя
########################################################################################################################
# кнопки добавления и просмотра
def video_url_and_favorites_list_button_creator(film_movie_url: str):
    markup = InlineKeyboardMarkup()
    film_id: int = get_movie_id_by_movie_video_url(film_movie_url)
    if film_movie_url is None:
        markup.add(
            InlineKeyboardButton(add_to_favorites_text, callback_data=film_id)
        )
    else:
        markup.add(
            InlineKeyboardButton(add_to_favorites_text, callback_data=film_id),
            InlineKeyboardButton(view_link_text, url=film_movie_url)
        )
    return markup


#  кнопка следующая страница
def next_button_creator(page_number: str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(next_button_text, callback_data=page_number))
    return markup


# команды без state
########################################################################################################################
@bot.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_contact(chat_id=message.chat.id, first_name='Глеб', phone_number='+79061337450')
    full_name: str = message.from_user.full_name
    add_user(user_id=message.from_user.id, username=message.from_user.username, full_name=full_name)
    message_for_user: str = f'<b>Привет, {full_name} Этот бот показывает фильмы по запросу попробуй</b>'
    await bot.send_message(message.chat.id,
                           message_for_user,
                           parse_mode='html')


# команда для отправления топа фильмов
@bot.message_handler(commands=['top'])
async def send_top_film(message: types.Message):
    try:
        page_number = 1
        billboard = KinoPoisk().give_top_films(page_number)
        for film_info in billboard.send_message_in_tg():
            for key, value in film_info.items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=video_url_and_favorites_list_button_creator(str(key)))

        await  bot.send_message(message.chat.id,
                                attention_text,
                                disable_notification=True,
                                reply_markup=next_button_creator(str(page_number + 1)))
    except Exception as e:
        print(traceback.format_exc())


@bot.message_handler(commands=['favorites'])
async def send_favorites_film(message: types.Message):
    try:
        list_movie_id = get_list_favorite_movies_by_user_id(message.from_user.id)
        for movie_id in list_movie_id:
            for i in get_movie_by_movie_id(movie_id):
                for key, value in i.items():
                    await bot.send_message(message.chat.id,
                                           value,
                                           parse_mode='html',
                                           disable_notification=True,
                                           reply_markup=video_url_and_favorites_list_button_creator(str(key)))

    except Exception as e:
        print(traceback.format_exc())


# команды со state
########################################################################################################################
# команда для отправления аналогов фильма
@bot.message_handler(commands=['recommendation'])
async def handler_send_recommendation(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Movie.name, message.chat.id)
    await bot.send_message(message.chat.id,
                           enter_movie_title_text,
                           reply_to_message_id=message.message_id,
                           reply_markup=force_reply)


@bot.message_handler(state=Movie.name)
async def send_recommendation(message: types.Message):
    try:
        film_name = message.text.lower().capitalize()
        message_for_user = if_like_text.format(film_name)
        await bot.send_message(message.chat.id, message_for_user)
        list_similar_films = KinoPoisk().give_recommendations(str(film_name))
        for film in list_similar_films:
            for key, value in film.send_info_about_film().items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=video_url_and_favorites_list_button_creator(str(key)))
    except Exception as e:
        print(traceback.format_exc())
    await bot.delete_state(message.from_user.id, message.chat.id)


# команда поиск фильма по ключевому слову (не фраза)
@bot.message_handler(commands=['search'])
async def handler_send_film_by_keyword(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Keyword.word, message.chat.id)
    await bot.send_message(message.chat.id,
                           enter_key_word_text,
                           reply_to_message_id=message.message_id,
                           reply_markup=force_reply)


@bot.message_handler(state=Keyword.word)
async def send_film_by_keyword(message: types.Message):
    page_number = 1
    try:
        keyword = message.text.lower().capitalize()
        billboard = KinoPoisk().give_films_by_keyword(keyword=str(keyword), page_number=page_number)
        for film_info in billboard.send_message_in_tg():
            for key, value in film_info.items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=video_url_and_favorites_list_button_creator(str(key)))
    except Exception as e:
        print(traceback.format_exc())
    await bot.delete_state(message.from_user.id, message.chat.id)


#  команда поиск фильмов (предысторий и сиквелов)
@bot.message_handler(commands=['story'])
async def handler_send_background(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Keyword.word, message.chat.id)
    await bot.send_message(message.chat.id,
                           enter_movie_title_text,
                           reply_to_message_id=message.message_id,
                           reply_markup=force_reply)

@bot.message_handler(state=Cinematography.name)
async def send_background(message: types.Message):
    film_name = message.text.lower().capitalize()
    try:
        for film in KinoPoisk().send_spin_offs(film_name):
            for key, value in film.send_info_about_film().items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=video_url_and_favorites_list_button_creator(str(key)))
    except Exception as e:
        print(traceback.format_exc())
    await bot.delete_state(message.from_user.id, message.chat.id)


#  кнопочки
@bot.callback_query_handler(func=lambda call: call.data.isdigit() == True)
async def callback_query(call):
    digit = call.data
    if len(digit) == 1:
        kino = KinoPoisk()
        page_number = int(digit)
        billboard = kino.give_top_films(page_number)
        for film_info in billboard.send_message_in_tg():
            for key, value in film_info.items():
                await bot.send_message(call.message.chat.id,
                                       value,
                                       parse_mode='html',
                                       disable_notification=True,
                                       reply_markup=video_url_and_favorites_list_button_creator(str(key)))
        await  bot.send_message(call.message.chat.id,
                                attention_text,
                                disable_notification=True,
                                reply_markup=next_button_creator(str(page_number + 1)))
    else:
        add_favourite_movie(user_id=call.from_user.id, movie_id=int(digit))

    await bot.send_message(call.message.chat.id, add_a_movie_to_favorites_text, disable_notification=True)


#  поиск фильмов
@bot.message_handler(func=lambda message: True)
async def send_film_by_film_name(message):
    query_film: str = message.text.lower().capitalize()
    logger.info(query_film)
    links = get_movie_by_film_title(query_film)
    # DB
    if links:
        for link in links:
            for key, value in link.items():
                await bot.send_message(message.chat.id,
                                       value,
                                       parse_mode='html',
                                       reply_markup=video_url_and_favorites_list_button_creator(key))
        return
    # API
    else:
        try:
            links = VX().get_film_link_by_name(query_film)
            if links:
                for link in links:
                    for key, value in link.items():
                        await bot.send_message(message.chat.id,
                                               value,
                                               parse_mode='html',
                                               reply_markup=video_url_and_favorites_list_button_creator(key))
            else:
                await  bot.send_message(message.chat.id,
                                        sorry_film_did_not_fild_text,
                                        parse_mode='html')
        except Exception as e:
            print(traceback.format_exc())


if __name__ == '__main__':
    with models.db:
        models.db.create_tables([models.User, models.User2Movie, models.Movie])

    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.add_custom_filter(asyncio_filters.IsDigitFilter())

    asyncio.run(bot.polling(none_stop=True))
