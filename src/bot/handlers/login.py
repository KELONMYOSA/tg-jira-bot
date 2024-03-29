from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.db.dao import Database


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["login"])
    async def login(message: Message):
        with Database() as db:
            if db.is_authorized(message.from_user.id):
                await bot.send_message(
                    message.chat.id,
                    """
Вы уже авторизованны!

Для выхода из аккаунта - /logout
                        """,
                )
            else:
                await bot.send_message(message.chat.id, "Введите логин:")
                await bot.set_state(message.from_user.id, "jira_user", message.chat.id)
