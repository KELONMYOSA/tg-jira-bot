from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.db.dao import Database


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["logout"])
    async def logout(message: Message):
        with Database() as db:
            db.remove_user(message.from_user.id)
        await bot.send_message(message.chat.id, "Вы более не авторизованы!")
