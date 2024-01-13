from fastapi import APIRouter, Request

from src.bot.app import bot
from src.db.dao import Database

router = APIRouter()


@router.post("/jira/webhook")
async def webhook(request: Request):
    r = await request.json()
    if r["webhookEvent"] == "jira:issue_created":
        issue = r["issue"]
        key = issue["key"]
        summary = issue["fields"]["summary"]
        priority = issue["fields"]["priority"]["name"]
        description = issue["fields"]["description"]
        assignee = issue["fields"]["assignee"]["name"]

        with Database() as db:
            tg_users = db.get_tg_users(assignee)
            for tg_user in tg_users:
                try:
                    await bot.send_message(
                        tg_user[0],
                        f"""
Была создана новая задача с Вашим участием: 
                            
Ключ: {key}
Название: {summary}
Приоритет: {priority}
Описание: {description}
                        """,
                    )
                except:
                    print(f"Unable to send a message to {tg_user[1]}")

    return {"status": "success"}
