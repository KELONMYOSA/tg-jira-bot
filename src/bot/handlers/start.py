from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["start"])
    async def start_bot(message: Message):
        await bot.send_message(
            message.chat.id,
            """
Привет!

Я - бот компании Комфортел, создан для того, чтобы упростить взаимодействие с Jira.
Я могу помочь тебе создать, найти и открыть задачу, а также напишу, когда будет создана задача для тебя.

Но для начала необходимо авторизоваться:
            """,
        )
        await bot.send_message(message.chat.id, "Введите логин:")
        await bot.set_state(message.from_user.id, "jira_user", message.chat.id)
