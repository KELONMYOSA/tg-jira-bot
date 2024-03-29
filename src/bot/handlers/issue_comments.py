import re
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
        all_button = False

        if not comments:
            message_text = f"Комментарии к задаче {issue_key} отсутствуют"
        else:
            if len(comments) > 3:
                message_text = f"Последние комментарии к задаче {issue_key}:\n\n"
                comments = comments[-3:]
                all_button = True
            else:
                message_text = f"Комментарии к задаче {issue_key}:\n\n"
            for comment in comments:
                input_datetime = datetime.strptime(comment.created, "%Y-%m-%dT%H:%M:%S.%f%z")
                output_datetime = input_datetime.strftime("%d.%m в %H:%M")
                text_to_add = f"{output_datetime} - {comment.author.displayName} ({comment.author.name}):\n"
                text_to_add += comment.body + "\n\n"
                if len(text_to_add) > 4000:
                    cut = 4000 - len(message_text)
                    message_text += text_to_add[:cut]
                    await bot.send_message(call.message.chat.id, message_text, disable_web_page_preview=True)
                    message_text = text_to_add[cut:]
                elif len(message_text) + len(text_to_add) < 4000:
                    message_text += text_to_add
                else:
                    await bot.send_message(call.message.chat.id, message_text, disable_web_page_preview=True)
                    message_text = text_to_add

        keyboard = InlineKeyboardMarkup()
        new_comment_button = InlineKeyboardButton("Написать", callback_data=f"comments_issue_new_{issue_key}")
        if all_button:
            all_comments_button = InlineKeyboardButton(
                "Показать все", callback_data=f"comments_issue_all_{issue_key}_|_yes"
            )
            keyboard.add(all_comments_button, new_comment_button)
        else:
            keyboard.add(new_comment_button)
        await bot.send_message(call.message.chat.id, message_text, reply_markup=keyboard, disable_web_page_preview=True)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("comments_issue_all_"))
    async def comments_issue_all(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        issue_key, delete = call.data.replace("comments_issue_all_", "").split("_|_")

        if delete == "yes":
            await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        comments = jira.comments(issue_key)

        message_text = f"Комментарии к задаче {issue_key}:\n\n"
        for comment in comments:
            input_datetime = datetime.strptime(comment.created, "%Y-%m-%dT%H:%M:%S.%f%z")
            output_datetime = input_datetime.strftime("%d.%m в %H:%M")
            text_to_add = f"{output_datetime} - {comment.author.displayName} ({comment.author.name}):\n"
            text_to_add += comment.body + "\n\n"
            if len(text_to_add) > 4000:
                cut = 4000 - len(message_text)
                message_text += text_to_add[:cut]
                await bot.send_message(call.message.chat.id, message_text, disable_web_page_preview=True)
                message_text = text_to_add[cut:]
            elif len(message_text) + len(text_to_add) < 4000:
                message_text += text_to_add
            else:
                await bot.send_message(call.message.chat.id, message_text, disable_web_page_preview=True)
                message_text = text_to_add

        keyboard = InlineKeyboardMarkup()
        new_comment_button = InlineKeyboardButton("Написать", callback_data=f"comments_issue_new_{issue_key}")
        keyboard.add(new_comment_button)
        await bot.send_message(call.message.chat.id, message_text, reply_markup=keyboard, disable_web_page_preview=True)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("comments_issue_new_"))
    async def comments_issue_new(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "Введите текст комментария:")
        await bot.set_state(call.message.chat.id, call.data, call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("comments_issue_reply_"))
    async def comments_issue_reply(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.message.chat.id, "Введите текст комментария:")
        await bot.set_state(call.message.chat.id, call.data, call.message.chat.id)


async def comments_issue_new_text(message: Message, issue_key: str):
    comment_text = message.text.strip()

    credentials = await get_credentials(message.from_user.id)
    if credentials is None:
        return
    jira = jira_auth(*credentials)
    jira.add_comment(issue_key, comment_text)

    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.send_message(message.chat.id, f"Комментарий к задаче {issue_key} был добавлен")


async def comments_issue_reply_text(message: Message, issue_key: str, username: str):
    reply_text = f"[~{username}]\n{message.text.strip()}"

    credentials = await get_credentials(message.from_user.id)
    if credentials is None:
        return
    jira = jira_auth(*credentials)
    jira.add_comment(issue_key, reply_text)

    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.send_message(message.chat.id, f"Ответ на комментарий к задаче {issue_key} был добавлен")


async def comments_reply(chat_id: int, bot_text: str, user_text: str):
    issue_pattern = re.compile(r"задаче (\w+-\d+)")
    username_pattern = re.compile(r"\((\w+)\):")
    issue_match = issue_pattern.search(bot_text)
    username_match = username_pattern.search(bot_text)
    issue_key = issue_match.group(1) if issue_match else None
    username = username_match.group(1) if username_match else None

    if issue_key and username:
        reply_text = f"[~{username}]\n{user_text}"

        credentials = await get_credentials(chat_id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)
        jira.add_comment(issue_key, reply_text)

        await bot.send_message(chat_id, f"Ответ на комментарий к задаче {issue_key} был добавлен")
