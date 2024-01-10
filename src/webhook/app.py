from fastapi import FastAPI

from src.webhook.routers import router

app = FastAPI(
    title="Comfortel Jira Webhook",
    contact={"name": "KELONMYOSA", "url": "https://t.me/KELONMYOSA"},
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/docs/redoc",
)

app.include_router(router)
