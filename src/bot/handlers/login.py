from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["login"])
    async def login(message: Message):
        await bot.send_message(message.chat.id, "Введите логин:")
        await bot.set_state(message.from_user.id, "jira_user", message.chat.id)
