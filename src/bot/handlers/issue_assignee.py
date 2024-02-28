from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.dict import build_name2displayName, executor_name2displayName
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("assignee_issue_select_"))
    async def assignee_issue_select(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        issue_key = call.data.replace("assignee_issue_select_", "")

        keyboard_buttons = []
        for name in executor_name2displayName:
            keyboard_buttons.append(
                InlineKeyboardButton(
                    executor_name2displayName[name], callback_data=f"assignee_issue_change_{issue_key}_|_{name}"
                )
            )
        keyboard = InlineKeyboardMarkup(row_width=1).add(*keyboard_buttons)
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="assignee_issue_cancel"))

        await bot.send_message(
            call.message.chat.id, f"Изменение исполнителя задачи {issue_key}:", reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "assignee_issue_cancel")
    async def assignee_issue_cancel(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("assignee_issue_change_"))
    async def assignee_issue_change(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key, assignee = call.data.replace("assignee_issue_change_", "").split("_|_")

        if assignee == "build":
            keyboard_buttons = []
            for name in build_name2displayName:
                keyboard_buttons.append(
                    InlineKeyboardButton(
                        build_name2displayName[name], callback_data=f"assignee_issue_change_{issue_key}_|_{name}"
                    )
                )
            keyboard = InlineKeyboardMarkup(row_width=1).add(*keyboard_buttons)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)
            return

        await bot.delete_message(call.message.chat.id, call.message.id)

        issue = jira.issue(issue_key)
        issue.update(assignee={"name": assignee})

        await bot.send_message(
            call.message.chat.id, f"Исполнитель задачи {issue_key}: {jira.issue(issue_key).fields.assignee.displayName}"
        )
