from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.bot.handlers.issue_attachments import attachments_issue_new_file
from src.bot.handlers.issue_comments import comments_issue_new_text
from src.bot.handlers.issue_create import (
    create_issue_confirm,
    create_issue_description,
    create_issue_priority,
    create_issue_summary,
)
from src.bot.handlers.issues_search import search_issues_key
from src.bot.utils.dict import commands_list
from src.bot.utils.jira_auth import get_jira_pass, get_jira_user


def run(bot: AsyncTeleBot):
    @bot.message_handler(
        func=lambda message: message.text not in commands_list, content_types=["photo", "video", "document", "text"]
    )
    async def echo_all(message: Message):
        user_state = await bot.get_state(message.from_user.id, message.chat.id)

        if user_state is None:
            await bot.delete_message(message.chat.id, message.message_id)
            return

        # Получение логина для авторизации
        if user_state == "jira_user":
            await get_jira_user(message)
        # Получение пароля для авторизации
        elif user_state.startswith("jira_pass_"):
            jira_user = user_state.replace("jira_pass_", "")
            await get_jira_pass(message, jira_user)
        # Получение названия для создания задачи
        elif user_state.startswith("create_issue_summary_"):
            data = user_state.replace("create_issue_summary_", "").split("_|_")
            await create_issue_summary(message, *data)
        # Получение приоритета для создания задачи
        elif user_state.startswith("create_issue_priority_"):
            data = user_state.replace("create_issue_priority_", "").split("_|_")
            await create_issue_priority(message, *data)
        # Получение описания для создания задачи
        elif user_state.startswith("create_issue_description_"):
            data = user_state.replace("create_issue_description_", "").split("_|_")
            await create_issue_description(message, *data)
        # Получение подтверждения для создания задачи
        elif user_state.startswith("create_issue_confirm_"):
            data = user_state.replace("create_issue_confirm_", "").split("_|_")
            await create_issue_confirm(message, *data)
        # Получение текста для создания комментария
        elif user_state.startswith("comments_issue_new_"):
            issue_key = user_state.replace("comments_issue_new_", "")
            await comments_issue_new_text(message, issue_key)
        # Получение файл для отправки вложения
        elif user_state.startswith("attachments_issue_new_"):
            issue_key = user_state.replace("attachments_issue_new_", "")
            await attachments_issue_new_file(message, issue_key)
        # Получение текста для поиска задачи по ключу
        elif user_state == "search_issue":
            await search_issues_key(message)
