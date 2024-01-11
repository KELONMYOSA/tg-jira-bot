from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from src.bot.utils.jira_auth import get_jira_user, get_jira_pass


def run(bot: AsyncTeleBot):
    @bot.message_handler(func=lambda message: message.text not in ["/start", "/login"])
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
