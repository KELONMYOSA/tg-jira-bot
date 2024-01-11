from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.db.dao import Database


# Test method --- REMOVE!
def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["info"])
    async def my_info(message: Message):
        with Database() as db:
            if db.is_authorized(message.from_user.id):
                user_credentials = db.get_user(message.from_user.id)
                await bot.send_message(message.chat.id, ", ".join(user_credentials))
            else:
                await bot.send_message(
                    message.chat.id,
                    """
Необходимо авторизоваться!

Для авторизации - /login
                        """,
                )
