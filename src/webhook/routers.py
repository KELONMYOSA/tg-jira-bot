import re
from datetime import datetime

from fastapi import APIRouter, Request
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity

from src.bot.app import bot
from src.db.dao import Database

router = APIRouter()


@router.post("/jira/webhook")
async def webhook(request: Request):
    r = await request.json()
    issue = r["issue"]
    key = issue["key"]
    summary = issue["fields"]["summary"]
    status = issue["fields"]["status"]["name"]
    priority = issue["fields"]["priority"]["name"]
    description = issue["fields"]["description"]
    assignees = [issue["fields"]["assignee"]["name"]]

    message_header = None
    hlink = None
    message_body = f"""
Ключ: {key}
Название: {summary}
Статус: {status}
Приоритет: {priority}
Описание: {description}
                    """
    keyboard = InlineKeyboardMarkup()
    edit_issue_button = InlineKeyboardButton("Изменить", callback_data=f"edit_issue_{key}")
    comments_issue_button = InlineKeyboardButton("Комментарии", callback_data=f"comments_issue_get_{key}")
    attachments_issue_button = InlineKeyboardButton("Вложения", callback_data=f"attachments_issue_get_{key}")
    keyboard.add(edit_issue_button, comments_issue_button, attachments_issue_button)

    if r["webhookEvent"] == "jira:issue_created":
        message_header = "Была создана новая задача с Вашим участием:"
        hlink = MessageEntity(
            "text_link", len(message_header) + 8, len(key), f"https://jira.comfortel.pro/browse/{key}"
        )
    elif r["webhookEvent"] == "jira:issue_updated":
        if r["issue_event_type_name"] == "issue_updated":
            message_header = "Была обновлена задача с Вашим участием:"
            hlink = MessageEntity(
                "text_link", len(message_header) + 8, len(key), f"https://jira.comfortel.pro/browse/{key}"
            )
        elif r["issue_event_type_name"] == "issue_generic":
            message_header = "Был изменен статус задачи с Вашим участием:"
            hlink = MessageEntity(
                "text_link", len(message_header) + 8, len(key), f"https://jira.comfortel.pro/browse/{key}"
            )
        elif r["issue_event_type_name"] == "issue_assigned":
            message_header = "Вы были назначены исполнителем задачи:"
            hlink = MessageEntity(
                "text_link", len(message_header) + 8, len(key), f"https://jira.comfortel.pro/browse/{key}"
            )
        elif "comment" in r:
            comment = r["comment"]
            comment_text = comment["body"]

            mentioned_users = re.findall(r"\[~([^]]+)]", comment_text)
            assignees = mentioned_users

            input_datetime = datetime.strptime(comment["created"], "%Y-%m-%dT%H:%M:%S.%f%z")
            output_datetime = input_datetime.strftime("%d.%m в %H:%M")
            message_body = f"{output_datetime} - {comment['author']['displayName']} ({comment['author']['name']}):\n"
            message_body += comment_text

            keyboard = InlineKeyboardMarkup()
            new_comment_button = InlineKeyboardButton("Написать", callback_data=f"comments_issue_new_{key}")
            keyboard.add(new_comment_button)

            if r["issue_event_type_name"] == "issue_commented":
                message_header = f"Вы были упомянуты в комментарии к задаче {key}:\n"
                hlink = MessageEntity("text_link", 41, len(key), f"https://jira.comfortel.pro/browse/{key}")
            elif r["issue_event_type_name"] == "issue_comment_edited":
                message_header = f"Был изменен комментарий к задаче {key} с Вашим упоминанием:\n"
                hlink = MessageEntity("text_link", 33, len(key), f"https://jira.comfortel.pro/browse/{key}")

    if message_header is not None:
        with Database() as db:
            tg_users = []
            for assignee in assignees:
                tg_users.extend(db.get_tg_users(assignee))
            for tg_user in tg_users:
                try:
                    await bot.send_message(
                        tg_user[0], message_header + "\n" + message_body, reply_markup=keyboard, entities=[hlink]
                    )
                except:
                    print(f"Unable to send a message to {tg_user[1]}")

    return {"status": "success"}
