import asyncio
import os
import re

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from KinoPoisk import KinoPoisk
from VX import VX

bot = AsyncTeleBot(os.getenv('telegram_token'))


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


@bot.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    first_name: str = message.from_user.first_name
    last_name: str = message.from_user.last_name
    message_for_user: str
    if last_name is None or last_name == 'None'.casefold():
        message_for_user = f'<b>Привет.{first_name}</b>'
    else:
        message_for_user = f'<b>Привет.{first_name} {last_name}</b>'

    await bot.send_message(message.chat.id, message_for_user, parse_mode='html')


def extract_arg(arg):
    return arg.split()[1:]


@bot.message_handler(commands=['recommendation'])
async def send_recommendation(message: types.Message):
    for film_name in extract_arg(message.text):
        message_for_user = 'Если вам понравился этот фильм Бот отправляет  похожие фильмы'.format(film_name)
        await bot.send_message(message.chat.id, message_for_user)
        list_similar_films = KinoPoisk().give_recommendations(str(film_name))
        for film in list_similar_films:
            await bot.send_message(message.chat.id, film.send_similar_films(), parse_mode='html')


# @bot.message_handler(commands=['topv2'])
# async def send_top_film_minimalistic(message: types.Message):
#     kino = KinoPoisk()
#     page_number = int(1)
#     billboard = kino.give_top_films(page_number)
#     await  bot.send_message(message.chat.id, billboard.send_message_in_tg_minimalistic(), parse_mode='html')


@bot.message_handler(commands=['top'])
async def send_top_film(message: types.Message):
    page_number = 1
    billboard = KinoPoisk().give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await bot.send_message(message.chat.id, value, parse_mode='html', disable_notification=True,
                                   reply_markup=webpage_and_favorites_list_add_handler(str(key)))

    await  bot.send_message(message.chat.id, 'Предлагаем вашему вниманию следующие  кинопроизведения',
                            disable_notification=True, reply_markup=next_button_handler(str(page_number + 1)))


@bot.message_handler(commands=['search'])
async def send_movies_with_criteria(message: types.Message):
    kino = KinoPoisk()
    page_number = 1
    billboard = kino.give_search_result_with_filter(year_max=2020, year_min= 2012,  page=page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await  bot.send_message(message.chat.id, value, parse_mode='html', disable_notification=True,
                                    reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    await  bot.send_message(message.chat.id, 'Предлагаем вашему вниманию следующие  кинопроизведения',
                            disable_notification=True,
                            reply_markup=next_button_handler('search' + str(page_number + 1)))


# обработка кнопок вот так происходит
# @bot.callback_query_handler(func=lambda call: str(call.data).startswith('788542'))
# async def callback_query(call):
#     await bot.send_message(call.message.chat.id, call.data)


@bot.callback_query_handler(func=lambda call: call.data.isdigit() == True)
async def callback_query(call):
    kino = KinoPoisk()
    page_number = int(call.data)
    billboard = kino.give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await bot.send_message(call.message.chat.id, value, parse_mode='html', disable_notification=True,
                                   reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    await  bot.send_message(call.message.chat.id, 'Предлагаем вашему вниманию следующие  кинопроизведения',
                            disable_notification=True, reply_markup=next_button_handler(str(page_number + 1)))


@bot.callback_query_handler(func=lambda call: str(call.data).startswith('search'))
async def callback_query(call):
    kino = KinoPoisk()
    digit_str = re.search('\d+', call.data).group()
    page_number = int(digit_str)
    billboard = kino.give_search_result_with_filter(page=page_number)
    for film_info in billboard.send_message_in_tg():
        for key, value in film_info.items():
            await  bot.send_message(call.message.chat.id, value, parse_mode='html', disable_notification=True,
                                    reply_markup=webpage_and_favorites_list_add_handler(str(key)))
    await  bot.send_message(call.message.chat.id, 'Предлагаем вашему вниманию следующие  кинопроизведения',
                            disable_notification=True,
                            reply_markup=next_button_handler('search' + str(page_number + 1)))


@bot.message_handler(func=lambda message: True)
async def send_film_by_film_name(message):
    links = VX().get_film_link_by_name(message.text)
    for link in links:
        for key, value in link.items():
            await bot.send_message(message.chat.id, value, parse_mode='html',
                                   reply_markup=webpage_and_favorites_list_add_handler(str(key)))


if __name__ == '__main__':
    asyncio.run(bot.polling(none_stop=True))
