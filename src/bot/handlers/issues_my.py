from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["my"])
    async def my_issues(message: Message):
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issues = jira.search_issues(f"assignee = '{credentials[0]}' or reporter = '{credentials[0]}' order by created")
        if not issues:
            await bot.send_message(message.chat.id, "Ваши задачи не были найдены!")
        else:
            await bot.send_message(message.chat.id, "Ваши задачи:")
            for issue in issues:
                keyboard = InlineKeyboardMarkup()
                edit_issue_button = InlineKeyboardButton("Изменить", callback_data=f"edit_issue_{issue.key}")
                comments_issue_button = InlineKeyboardButton(
                    "Комментарии", callback_data=f"comments_issue_get_{issue.key}"
                )
                attachments_issue_button = InlineKeyboardButton(
                    "Вложения", callback_data=f"attachments_issue_get_{issue.key}"
                )
                keyboard.add(edit_issue_button, comments_issue_button, attachments_issue_button)
                await bot.send_message(
                    message.chat.id,
                    f"""
Ключ: {issue.key}
Название: {issue.fields.summary}
Исполнитель: {issue.fields.assignee.displayName}
Статус: {issue.fields.status.name}
Приоритет: {issue.fields.priority.name}
Описание: {issue.fields.description}
                        """,
                    reply_markup=keyboard,
                )
