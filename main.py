import os

from ChangeLink import ChangeLink
from KinoPoisk import KinoPoisk

from telebot.async_telebot import AsyncTeleBot
from telebot import types
import asyncio

from VX import VX

bot = AsyncTeleBot(os.getenv('telegram_token'))


@bot.message_handler(commands=['start'])
async def send_welcome(message):
    first_name: str = message.from_user.first_name
    last_name: str = message.from_user.last_name
    message_for_user: str
    if last_name == 'None':
        message_for_user = f'<b>Привет.{first_name}</b>'
    else:
        message_for_user = f'<b>Привет.{first_name} {last_name}</b>'

    await bot.send_message(message.chat.id, message_for_user, parse_mode='html')


@bot.message_handler(commands=['top'])
async def send_top_film(message):
    kino = KinoPoisk()
    billboard = kino.give_top_films('0')
    await  bot.send_message(message.chat.id, billboard.do_html_code(), parse_mode='html')


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    vx = VX()
    film_link: str = vx.get_film_link(message.text)
    await bot.send_message(message.chat.id, film_link)


if __name__ == '__main__':
    asyncio.run(bot.polling(none_stop=True))
