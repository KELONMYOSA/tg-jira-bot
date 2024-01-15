from datetime import datetime

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.app import bot
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("comments_issue_get_"))
    async def comments_issue_get(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("comments_issue_get_", "")
        comments = jira.comments(issue_key)

        if not comments:
            message_text = f"Комментарии к задаче {issue_key} отсутствуют"
        else:
            message_text = f"Комментарии к задаче {issue_key}:\n\n"
            for comment in comments:
                input_datetime = datetime.strptime(comment.created, "%Y-%m-%dT%H:%M:%S.%f%z")
                output_datetime = input_datetime.strftime("%d.%m в %H:%M")
                message_text += f"{output_datetime} - {comment.author.displayName} ({comment.author.name}):\n"
                message_text += comment.body + "\n\n"

        keyboard = InlineKeyboardMarkup()
        new_comment_button = InlineKeyboardButton("Написать", callback_data=f"comments_issue_new_{issue_key}")
        keyboard.add(new_comment_button)
        await bot.send_message(call.message.chat.id, message_text, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("comments_issue_new_"))
    async def comments_issue_new(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        issue_key = call.data.replace("comments_issue_new_", "")

        await bot.send_message(call.message.chat.id, "Введите текст комментария:")
        await bot.set_state(call.message.chat.id, f"comments_issue_new_{issue_key}", call.message.chat.id)


async def comments_issue_new_text(message: Message, issue_key: str):
    text = message.text.strip()
    await bot.send_message(
        message.chat.id,
        f"""
{text}

Добавить этот комментарий к задаче {issue_key}? (Да/Нет)
        """,
    )
    await bot.set_state(message.from_user.id, f"comments_issue_confirm_{issue_key}_|_{text}", message.chat.id)


async def comments_issue_new_confirm(message: Message, issue_key: str, comment_text: str):
    confirm = message.text.strip().lower()
    if confirm == "да":
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)
        jira.add_comment(issue_key, comment_text)

        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, f"Комментарий к задаче {issue_key} был добавлен")
    elif confirm == "нет":
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, f"Отмена комментария к задаче {issue_key}")
    else:
        await bot.send_message(message.chat.id, "Введите Да или Нет:")
