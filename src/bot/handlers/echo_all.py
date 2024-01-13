from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.bot.handlers.create_issue import (
    create_issue_confirm,
    create_issue_description,
    create_issue_priority,
    create_issue_summary,
)
from src.bot.utils.dict import commands_list
from src.bot.utils.jira_auth import get_jira_pass, get_jira_user


def run(bot: AsyncTeleBot):
    @bot.message_handler(func=lambda message: message.text not in commands_list)
    async def echo_all(message: Message):
        user_state = await bot.get_state(message.from_user.id, message.chat.id)

        if user_state is None:
            await bot.delete_message(message.chat.id, message.message_id)
            return

        if user_state == "jira_user":
            await get_jira_user(message)
        elif user_state.startswith("jira_pass_"):
            jira_user = user_state.replace("jira_pass_", "")
            await get_jira_pass(message, jira_user)
        elif user_state == "create_issue_summary":
            await create_issue_summary(message)
        elif user_state.startswith("create_issue_priority_"):
            summary = user_state.replace("create_issue_priority_", "")
            await create_issue_priority(message, summary)
        elif user_state.startswith("create_issue_description_"):
            data = user_state.replace("create_issue_description_", "").split("_|_")
            await create_issue_description(message, *data)
        elif user_state.startswith("create_issue_confirm_"):
            data = user_state.replace("create_issue_confirm_", "").split("_|_")
            await create_issue_confirm(message, *data)
