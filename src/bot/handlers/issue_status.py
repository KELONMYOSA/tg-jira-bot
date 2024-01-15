from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.callback_query_handler(func=lambda call: call.data.startswith("status_issue_select_"))
    async def status_issue_select(call: CallbackQuery):
        await bot.answer_callback_query(call.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("status_issue_select_", "")
        transitions = jira.transitions(issue_key)

        keyboard_buttons = []
        for trans in transitions:
            keyboard_buttons.append(
                InlineKeyboardButton(trans["name"], callback_data=f"status_issue_change_{issue_key}_|_{trans['id']}")
            )
        keyboard_buttons.append(
            InlineKeyboardButton("Удалить задачу", callback_data=f"status_issue_delete_{issue_key}")
        )
        keyboard = InlineKeyboardMarkup().add(*keyboard_buttons)
        keyboard.add(InlineKeyboardButton("Отмена", callback_data="status_issue_cancel"))

        await bot.send_message(
            call.message.chat.id, f"Изменение статуса для задачи {issue_key}:", reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data == "status_issue_cancel")
    async def status_issue_cancel(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status_issue_change_"))
    async def status_issue_change(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key, transition = call.data.replace("status_issue_change_", "").split("_|_")
        jira.transition_issue(issue_key, transition)

        await bot.send_message(
            call.message.chat.id, f"Статус задачи {issue_key}: {jira.issue(issue_key).fields.status.name}"
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status_issue_delete_"))
    async def status_issue_delete(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        issue_key = call.data.replace("status_issue_delete_", "")
        keyboard = InlineKeyboardMarkup()
        success_button = InlineKeyboardButton("Да", callback_data=f"status_issue_deleteYes_{issue_key}")
        cancel_button = InlineKeyboardButton("Нет", callback_data=f"status_issue_deleteNo_{issue_key}")
        keyboard.add(success_button, cancel_button)
        await bot.send_message(call.message.chat.id, "Вы действительно хотите удалить задачу?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status_issue_deleteYes_"))
    async def status_issue_delete_yes(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("status_issue_deleteYes_", "")
        issue = jira.issue(issue_key)
        issue.delete()

        await bot.send_message(call.message.chat.id, f"Задача {issue_key} была удалена")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("status_issue_deleteNo_"))
    async def status_issue_delete_no(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        issue_key = call.data.replace("status_issue_deleteNo_", "")

        await bot.send_message(call.message.chat.id, f"Отмена закрытия задачи {issue_key}")
