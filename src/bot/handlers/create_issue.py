from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.bot.app import bot
from src.bot.utils.dict import priority2text
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["create"])
    async def create_issue(message: Message):
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        await bot.send_message(message.chat.id, "Создание задачи. Введите название задачи:")
        await bot.set_state(message.from_user.id, "create_issue_summary", message.chat.id)


async def create_issue_summary(message: Message):
    summary = message.text.strip()
    await bot.send_message(message.chat.id, "Введите приоритет задачи (1 - Минимальный, 5 - Наивысший):")
    await bot.set_state(message.from_user.id, f"create_issue_priority_{summary}", message.chat.id)


async def create_issue_priority(message: Message, summary: str):
    priority = message.text.strip()
    if priority not in priority2text:
        await bot.send_message(message.chat.id, "Это должно быть число от 1 до 5:")
    else:
        await bot.send_message(message.chat.id, "Введите описание задачи:")
        await bot.set_state(message.from_user.id, f"create_issue_description_{summary}_|_{priority}", message.chat.id)


async def create_issue_description(message: Message, summary: str, priority: str):
    priority_text = priority2text[priority]
    description = message.text.strip()
    await bot.send_message(
        message.chat.id,
        f"""
Проект: TEST1
Название: {summary}
Приоритет: {priority_text}
Описание: {description}

Создать задачу? (Да/Нет)
        """,
    )
    await bot.set_state(
        message.from_user.id, f"create_issue_confirm_{summary}_|_{priority}_|_{description}", message.chat.id
    )


async def create_issue_confirm(message: Message, summary: str, priority: str, description: str):
    confirm = message.text.strip().lower()
    if confirm == "да":
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)
        issue = jira.create_issue(
            project="TEST1",
            summary=summary,
            issuetype={"name": "Задача"},
            priority={"name": priority2text[priority]},
            description=description,
        )
        await bot.send_message(message.chat.id, f"Задача {issue.key} создана")
    elif confirm == "нет":
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, "Создание задачи отменено")
    else:
        await bot.send_message(message.chat.id, "Введите Да или Нет:")
