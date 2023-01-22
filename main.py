import asyncio
import os
import re
import traceback

from telebot import asyncio_filters
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from Model import models
from VX import VX
from checkRightWriting import check_text_for_correct_spelling
from kinoPoisk import KinoPoisk
from messages import *
from states import Movie, Keyword, Cinematography

bot = AsyncTeleBot(os.getenv('telegram_token'), state_storage=StateMemoryStorage())


# кнопки для пользователя
########################################################################################################################
# кнопки добавления и просмотра
# def webpage_and_favorites_list_add_handler(message: types.Message, film_id: str):
def webpage_and_favorites_list_add_handler(film_id: str):
    markup = InlineKeyboardMarkup()
    film_id = re.search('\d+', film_id).group(0)
    film_link = VX().get_film_link_by_kinopoisk_id(int(film_id))
    if film_link is None:
        markup.add(InlineKeyboardButton(add_to_favorites, callback_data=film_id))
    else:
        markup.add(InlineKeyboardButton(add_to_favorites, callback_data=film_id),
                   InlineKeyboardButton(view_link, url=film_link))
    return markup


#  кнопка следующая страница
def next_button_handler(page_number: str):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(next, callback_data=page_number))
    return markup


# команды без state
########################################################################################################################
@bot.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    full_name: str = message.from_user.full_name
    username = message.from_user.username
    #  добавления пользователя в базу
    with models.db:
        user = models.User(user_id=user_id, username=username, full_name=full_name).save(force_insert=True)

    message_for_user: str = f'<b>Привет, {full_name} Этот бот показывает фильмы по запросу попробуй</b>'

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
                            attention,
                            disable_notification=True,
                            reply_markup=next_button_handler(str(page_number + 1)))


# команды со state
########################################################################################################################
# команда для отправления аналогов фильма
@bot.message_handler(commands=['recommendation'])
async def handler_send_recommendation(message: types.Message):
    force_reply = types.ForceReply(True)
    await bot.set_state(message.from_user.id, Movie.name, message.chat.id)
    await bot.send_message(message.chat.id,
                           enter_movie_title,
                           reply_to_message_id=message.message_id,
                           reply_markup=force_reply)


@bot.message_handler(state=Movie.name)
async def send_recommendation(message: types.Message):
    try:
        film_name = message.text
        message_for_user = if_like.format(film_name)
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
    await bot.send_message(message.chat.id,
                           enter_key_word,
                           reply_to_message_id=message.message_id,
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
    await bot.send_message(message.chat.id,
                           enter_movie_title,
                           reply_to_message_id=message.message_id,
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
        print(traceback.format_exc())


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
                            attention,
                            disable_notification=True,
                            reply_markup=next_button_handler(str(page_number + 1)))


#  поиск фильмов
@bot.message_handler(func=lambda message: True)
async def send_film_by_film_name(message):
    query_film: str = message.text.lower()
    normal_message = check_text_for_correct_spelling(query_film)
    if normal_message is not None:
        try:
            links = VX().get_film_link_by_name(normal_message)
            if links:
                for link in links:
                    for key, value in link.items():
                        await bot.send_message(message.chat.id,
                                               value,
                                               parse_mode='html',
                                               reply_markup=webpage_and_favorites_list_add_handler(str(key)))
            else:
                await  bot.send_message(message.chat.id,
                                        sorry_film_did_not_fild,
                                        parse_mode='html')
        except Exception as e:
            print(traceback.format_exc())
    else:
        await  bot.send_message(message.chat.id,
                                sorry_film_title_wrong,
                                parse_mode='html')


if __name__ == '__main__':
    with models.db:
        models.db.create_tables([models.User, models.User2Movie, models.Movie])
    bot.add_custom_filter(asyncio_filters.StateFilter(bot))
    bot.add_custom_filter(asyncio_filters.IsDigitFilter())

    asyncio.run(bot.polling(none_stop=True))
