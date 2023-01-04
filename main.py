import os

from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio

from KinoPoisk import KinoPoisk
from VX import VX
from kinopoisk.movie import Movie

bot = AsyncTeleBot(os.getenv('telegram_token'))


def markup_inline(title: str, page_number: str):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(title, callback_data=page_number))
    return markup


@bot.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    first_name: str = message.from_user.first_name
    last_name: str = message.from_user.last_name
    message_for_user: str
    if last_name == 'None':
        message_for_user = f'<b>Привет.{first_name}</b>'
    else:
        message_for_user = f'<b>Привет.{first_name} {last_name}</b>'

    await bot.send_message(message.chat.id, message_for_user, parse_mode='html')


#  не работает пока что
# @bot.message_handler(commands=['recommendation'])
# async def send_recommendation(message: types.Message):
#     message_for_user = 'Рекомендация основывается  на каком то фильме.' \
#                        'Введите названия фильма который вам нравится и  бот отправит схожий фильм.'
#     await bot.send_message(message.chat.id, message_for_user)
#     film_name = message.text
#     kino = KinoPoisk()
#     for i in kino.give_recommendations(film_name):
#         await bot.send_message(message.chat.id, i.send_message_in_tg())


@bot.message_handler(commands=['top'])
async def send_top_film(message: types.Message):
    kino = KinoPoisk()
    page_number = int(1)
    billboard = kino.give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        await bot.send_message(message.chat.id, film_info)

    await  bot.send_message(message.chat.id, 'Предлагаем вашему вниманию следующие двадцать кинопроизведений',
                            reply_markup=markup_inline('Следующий', str(page_number + 1)))


@bot.callback_query_handler(func=lambda message: True)
async def callback_query(call):
    kino = KinoPoisk()
    page_number = int(call.data)
    billboard = kino.give_top_films(page_number)
    for film_info in billboard.send_message_in_tg():
        await bot.send_message(call.message.chat.id, film_info)

    await  bot.send_message(call.message.chat.id, 'Предлагаем вашему вниманию следующие двадцать кинопроизведений',
                            reply_markup=markup_inline('Следующий', str(page_number + 1)))


@bot.message_handler(func=lambda message: True)
async def send_film_by_film_name(message):
    film_link: str = VX().get_film_link_by_name(message.text)
    await bot.send_message(message.chat.id, film_link)


if __name__ == '__main__':
    asyncio.run(bot.polling(none_stop=True))
