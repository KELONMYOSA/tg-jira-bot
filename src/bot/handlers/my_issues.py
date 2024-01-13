from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["my"])
    async def my_issues(message: Message):
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issues = jira.search_issues(f"assignee was '{credentials[0]}' or reporter was '{credentials[0]}'")
        if not issues:
            await bot.send_message(message.chat.id, "Ваши задачи не были найдены!")
        else:
            await bot.send_message(message.chat.id, "Ваши задачи:")
            for issue in issues:
                await bot.send_message(
                    message.chat.id,
                    f"""
Ключ: {issue.key}
Название: {issue.fields.summary}
Приоритет: {issue.fields.priority.name}
Описание: {issue.fields.description}
                        """,
                )