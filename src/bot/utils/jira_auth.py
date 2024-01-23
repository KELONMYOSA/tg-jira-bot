from jira import JIRA
from telebot.types import Message

from src.bot.app import bot
from src.config import settings
from src.db.dao import Database


async def get_jira_user(message: Message):
    jira_user = message.text.strip()
    await bot.delete_message(message.chat.id, message.id)
    await bot.send_message(message.chat.id, "********")

    with Database() as db:
        registered_tg_user = db.get_registered_tg_user(jira_user)
    if registered_tg_user is not None and registered_tg_user != message.from_user.id:
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, "К данному логину привязан другой пользователь telegram!")
        return

    await bot.send_message(message.chat.id, "Введите пароль или API-ключ:")
    await bot.set_state(message.from_user.id, f"jira_pass_{jira_user}", message.chat.id)


async def get_jira_pass(message: Message, jira_user: str):
    jira_pass = message.text.strip()
    await bot.delete_message(message.chat.id, message.id)
    await bot.send_message(message.chat.id, "********")
    await bot.delete_state(message.from_user.id, message.chat.id)
    jira = jira_auth(jira_user, jira_pass)
    if jira is None:
        await bot.send_message(
            message.chat.id,
            """
Неверный логин или пароль!

Для повторной авторизации - /login
                               """,
        )
    else:
        with Database() as db:
            db.set_user(message.from_user.id, message.from_user.username, jira_user, jira_pass)
            db.register_user(message.from_user.id, message.from_user.username, jira_user)
        await bot.send_message(message.chat.id, "Вы успешно авторизованы!")


def jira_auth(login: str, password: str) -> JIRA | None:
    jira_options = {"server": settings.JIRA_URL}
    try:
        jira = JIRA(options=jira_options, basic_auth=(login, password))
        return jira
    except:
        return None


async def get_credentials(tg_user_id: id) -> tuple | None:
    with Database() as db:
        if db.is_authorized(tg_user_id):
            user_credentials = db.get_user(tg_user_id)
            return user_credentials
        else:
            await bot.send_message(
                tg_user_id,
                """
Необходимо авторизоваться!

Для авторизации - /login
                    """,
            )
            return None
