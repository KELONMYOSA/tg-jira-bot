from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, MessageEntity

from src.bot.app import bot
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["search"])
    async def search_issues(message: Message):
        await bot.send_message(message.chat.id, "Введите ключ задачи:")
        await bot.set_state(message.from_user.id, "search_issue", message.chat.id)


async def search_issues_key(message: Message):
    credentials = await get_credentials(message.from_user.id)
    if credentials is None:
        return
    jira = jira_auth(*credentials)

    issue_key = message.text.strip()
    issues = jira.search_issues(f"key = '{issue_key}'")

    await bot.delete_state(message.from_user.id, message.chat.id)
    if not issues:
        await bot.send_message(message.chat.id, "Задача не была найдена!")
    else:
        for issue in issues:
            keyboard = InlineKeyboardMarkup()
            edit_issue_button = InlineKeyboardButton("Изменить", callback_data=f"edit_issue_{issue.key}")
            comments_issue_button = InlineKeyboardButton("Комментарии", callback_data=f"comments_issue_get_{issue.key}")
            attachments_issue_button = InlineKeyboardButton(
                "Вложения", callback_data=f"attachments_issue_get_{issue.key}"
            )
            keyboard.add(edit_issue_button, comments_issue_button, attachments_issue_button)
            hlink = MessageEntity("text_link", 7, len(issue.key), f"https://jira.comfortel.pro/browse/{issue.key}")
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
                entities=[hlink],
            )
