from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.app import bot
from src.bot.utils.dict import build_name2displayName, executor_name2displayName, priority2text
from src.bot.utils.jira_auth import get_credentials, jira_auth


def run(bot: AsyncTeleBot):
    @bot.message_handler(commands=["create"])
    async def create_issue(message: Message):
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)
        projects = jira.projects()

        keyboard_buttons = []
        for project in projects:
            keyboard_buttons.append(
                InlineKeyboardButton(project.name, callback_data=f"create_issue_project_{project.key}")
            )
        keyboard = InlineKeyboardMarkup(row_width=1).add(*keyboard_buttons)

        await bot.send_message(message.chat.id, "Создание задачи. Выберите проект:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("create_issue_project_"))
    async def create_issue_project(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        project_key = call.data.replace("create_issue_project_", "")
        await bot.send_message(call.message.chat.id, f"Проект - {project_key}")

        keyboard_buttons = []
        for name in executor_name2displayName:
            keyboard_buttons.append(
                InlineKeyboardButton(
                    executor_name2displayName[name], callback_data=f"create_issue_executor_{project_key}_|_{name}"
                )
            )
        keyboard = InlineKeyboardMarkup(row_width=1).add(*keyboard_buttons)

        await bot.send_message(call.message.chat.id, "Выберите исполнителя:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("create_issue_executor_"))
    async def create_issue_executor(call: CallbackQuery):
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.message.chat.id, call.message.id)

        project_key, executor = call.data.replace("create_issue_executor_", "").split("_|_")

        if executor == "build":
            keyboard_buttons = []
            for name in build_name2displayName:
                keyboard_buttons.append(
                    InlineKeyboardButton(
                        build_name2displayName[name], callback_data=f"create_issue_executor_{project_key}_|_{name}"
                    )
                )
            keyboard = InlineKeyboardMarkup(row_width=1).add(*keyboard_buttons)
            await bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)
            return

        name2display_name = executor_name2displayName | build_name2displayName
        await bot.send_message(call.message.chat.id, f"Исполнитель - {name2display_name[executor]}")
        await bot.send_message(call.message.chat.id, "Введите название задачи:")
        await bot.set_state(
            call.message.chat.id, f"create_issue_summary_{project_key}_|_{executor}", call.message.chat.id
        )


async def create_issue_summary(message: Message, project_key: str, executor: str):
    summary = message.text.strip()
    await bot.send_message(message.chat.id, "Введите приоритет задачи (1 - Минимальный, 5 - Наивысший):")
    await bot.set_state(
        message.from_user.id, f"create_issue_priority_{project_key}_|_{executor}_|_{summary}", message.chat.id
    )


async def create_issue_priority(message: Message, project_key: str, executor: str, summary: str):
    priority = message.text.strip()
    if priority not in priority2text:
        await bot.send_message(message.chat.id, "Это должно быть число от 1 до 5:")
    else:
        await bot.send_message(message.chat.id, "Введите описание задачи:")
        await bot.set_state(
            message.from_user.id,
            f"create_issue_description_{project_key}_|_{executor}_|_{summary}_|_{priority}",
            message.chat.id,
        )


async def create_issue_description(message: Message, project_key: str, executor: str, summary: str, priority: str):
    priority_text = priority2text[priority]
    description = message.text.strip()
    name2display_name = executor_name2displayName | build_name2displayName
    await bot.send_message(
        message.chat.id,
        f"""
Проект: {project_key}
Исполнитель: {name2display_name[executor]}
Название: {summary}
Приоритет: {priority_text}
Описание: {description}

Создать задачу? (Да/Нет)
        """,
        disable_web_page_preview=True,
    )
    await bot.set_state(
        message.from_user.id,
        f"create_issue_confirm_{project_key}_|_{executor}_|_{summary}_|_{priority}_|_{description}",
        message.chat.id,
    )


async def create_issue_confirm(
    message: Message, project_key: str, executor: str, summary: str, priority: str, description: str
):
    confirm = message.text.strip().lower()
    if confirm == "да":
        credentials = await get_credentials(message.from_user.id)
        if credentials is None:
            return
        jira = jira_auth(*credentials)
        issue = jira.create_issue(
            project=project_key,
            assignee={"name": executor},
            summary=summary,
            issuetype={"name": "Задача"},
            priority={"name": priority2text[priority]},
            description=description,
        )
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, f"Задача {issue.key} создана")
    elif confirm == "нет":
        await bot.delete_state(message.from_user.id, message.chat.id)
        await bot.send_message(message.chat.id, "Создание задачи отменено")
    else:
        await bot.send_message(message.chat.id, "Введите Да или Нет:")
