from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit_issue_"))
    async def edit_issue(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        issue_key = call.data.replace("edit_issue_", "")

        assignee_button = InlineKeyboardButton("Исполнитель", callback_data=f"assignee_issue_select_{issue_key}")
        status_button = InlineKeyboardButton("Статус", callback_data=f"status_issue_select_{issue_key}")
        keyboard = InlineKeyboardMarkup().add(assignee_button, status_button)

        await bot.send_message(call.message.chat.id, f"Что изменить в задаче {issue_key}:", reply_markup=keyboard)
