from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.db.dao import Database


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["userlist"])
    async def userlist(message: Message):
        if message.from_user.username not in ["VladimirBut"]:
            await bot.send_message(message.chat.id, "Нет доступа к данной команде!")
            return

        with Database() as db:
            users = db.get_users_info()

        rows = []
        for user in users:
            rows.append(f"{user[0]}   {user[1]}   {user[2]}")

        text = "tg_user_id  |  tg_username  |  jira_login\n"
        text += "_________________________________________\n"
        text += str.join("\n", rows)
        text += "\n_________________________________________\n"
        text += f"Total users: {len(users)}"

        await bot.send_message(message.chat.id, text)
