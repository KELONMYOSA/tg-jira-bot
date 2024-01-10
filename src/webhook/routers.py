from fastapi import APIRouter

router = APIRouter()


@router.get("/webhook")
async def webhook():
    return {"message": "Success"}
