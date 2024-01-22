from jira.client import ResultList
from telebot.async_telebot import AsyncTeleBot
from telebot.formatting import hlink
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.app import bot
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["my"])
    async def my_issues(message: Message):
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issues = jira.search_issues(f"assignee = '{credentials[0]}' or reporter = '{credentials[0]}' order by created")
        if not issues:
            await bot.send_message(message.chat.id, "Ваши задачи не были найдены!")
        else:
            await my_issues_change_page(message.chat.id, 1, issues)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("my_issues_"))
    async def my_issues_pagination(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issues = jira.search_issues(f"assignee = '{credentials[0]}' or reporter = '{credentials[0]}' order by created")
        page_num = int(call.data.replace("my_issues_", ""))

        await my_issues_change_page(call.message.chat.id, page_num, issues)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("about_issue_"))
    async def about_issue(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        credentials = await get_credentials(call.message.chat.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)

        issue_key = call.data.replace("about_issue_", "")
        issue = jira.issue(issue_key)

        keyboard = InlineKeyboardMarkup()
        edit_issue_button = InlineKeyboardButton("Изменить", callback_data=f"edit_issue_{issue.key}")
        comments_issue_button = InlineKeyboardButton("Комментарии", callback_data=f"comments_issue_get_{issue.key}")
        attachments_issue_button = InlineKeyboardButton("Вложения", callback_data=f"attachments_issue_get_{issue.key}")
        keyboard.add(edit_issue_button, comments_issue_button, attachments_issue_button)
        await bot.send_message(
            call.message.chat.id,
            f"""
Ключ: {hlink(issue.key, 'https://jira.comfortel.pro/browse/' + issue.key)}
Название: {issue.fields.summary}
Исполнитель: {issue.fields.assignee.displayName}
Статус: {issue.fields.status.name}
Приоритет: {issue.fields.priority.name}
Описание: {issue.fields.description}
                """,
            reply_markup=keyboard,
            parse_mode="HTML",
        )


async def my_issues_change_page(chat_id: int, page_num: int, issues: ResultList, per_page: int = 5):
    message_rows = []
    issue_num_buttons = []
    n = 1 + (page_num - 1) * per_page
    for issue in issues[(page_num - 1) * per_page : page_num * per_page]:
        message_rows.append(f"{n}. {issue.fields.summary} ({issue.fields.assignee.name})")
        issue_num_buttons.append(InlineKeyboardButton(n, callback_data=f"about_issue_{issue.key}"))
        n += 1

    keyboard = InlineKeyboardMarkup(row_width=5).add(*issue_num_buttons)

    pagination_buttons = []
    if page_num > 1:
        pagination_buttons.append(InlineKeyboardButton("Назад", callback_data=f"my_issues_{page_num - 1}"))
    if len(issues) > page_num * per_page:
        pagination_buttons.append(InlineKeyboardButton("Далее", callback_data=f"my_issues_{page_num + 1}"))

    keyboard.add(*pagination_buttons)

    await bot.send_message(chat_id, str.join("\n", message_rows), reply_markup=keyboard)
