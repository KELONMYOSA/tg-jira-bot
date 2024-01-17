from io import BytesIO

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.app import bot
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("attachments_issue_get_"))
    async def attachments_issue_get(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("attachments_issue_get_", "")
        issue = jira.issue(issue_key, expand="changelog").raw
        attachments = {}
        for hist in issue["changelog"]["histories"]:
            for item in hist["items"]:
                if item["field"] == "Attachment":
                    if item["fromString"] is not None:
                        attachments[item["fromString"]] = item["from"]
                    if item["toString"] is not None:
                        attachments[item["toString"]] = item["to"]

        if attachments:
            await bot.send_message(call.message.chat.id, f"Вложения к задаче {issue_key}:")
        else:
            await bot.send_message(call.message.chat.id, f"Нет вложений к задаче {issue_key}")

        for file_name in attachments:
            await bot.send_document(
                call.message.chat.id, jira.attachment(attachments[file_name]).get(), visible_file_name=file_name
            )

        keyboard = InlineKeyboardMarkup()
        new_comment_button = InlineKeyboardButton("Отправить", callback_data=f"attachments_issue_new_{issue_key}")
        keyboard.add(new_comment_button)
        await bot.send_message(call.message.chat.id, "Добавить новое вложение?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("attachments_issue_new_"))
    async def attachments_issue_new(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        issue_key = call.data.replace("attachments_issue_new_", "")

        await bot.send_message(call.message.chat.id, "Отправьте только один файл (фото/документ):")
        await bot.set_state(call.message.chat.id, f"attachments_issue_new_{issue_key}", call.message.chat.id)


async def attachments_issue_new_file(message: Message, issue_key: str):
    credentials = await get_credentials(message.from_user.id)
    if credentials is None:
        return
    jira = jira_auth(*credentials)

    if message.document:
        file_info = await bot.get_file(message.document.file_id)
        file = BytesIO(await bot.download_file(file_info.file_path))
        jira.add_attachment(issue_key, file, message.document.file_name)

    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
        file = BytesIO(await bot.download_file(file_info.file_path))
        jira.add_attachment(issue_key, file, "tg_image.jpg")

    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.send_message(message.chat.id, f"Вложение к задаче {issue_key} было добавлено")
