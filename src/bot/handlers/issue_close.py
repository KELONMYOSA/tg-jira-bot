from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("close_issue_confirm_"))
    async def close_issue_confirm(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        issue_key = call.data.replace("close_issue_confirm_", "")
        keyboard = InlineKeyboardMarkup()
        success_button = InlineKeyboardButton("Да", callback_data=f"close_issue_success_{issue_key}")
        cancel_button = InlineKeyboardButton("Нет", callback_data=f"close_issue_cancel_{issue_key}")
        keyboard.add(success_button, cancel_button)
        await bot.send_message(call.message.chat.id, "Вы действительно хотите закрыть задачу?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("close_issue_success_"))
    async def close_issue_success(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("close_issue_success_", "")
        issue = jira.issue(issue_key)
        issue.delete()

        await bot.send_message(call.message.chat.id, f"Задача {issue_key} была закрыта")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("close_issue_cancel_"))
    async def close_issue_cancel(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        issue_key = call.data.replace("close_issue_cancel_", "")

        await bot.send_message(call.message.chat.id, f"Отмена закрытия задачи {issue_key}")
