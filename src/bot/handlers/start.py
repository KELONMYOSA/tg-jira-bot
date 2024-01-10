from telebot.types import Message


def run(bot):
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
