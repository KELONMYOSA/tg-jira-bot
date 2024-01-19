import asyncio

import uvicorn

from src.bot.app import init_bot, start_bot
from src.webhook.app import app


def start_uvicorn(loop):
    host = "0.0.0.0"
    port = 5555
    config = uvicorn.Config(app, host=host, port=port, loop=loop)
    server = uvicorn.Server(config)
    loop.run_until_complete(server.serve())


def start_tg_bot(loop):
    init_bot()
    loop.create_task(start_bot())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_tg_bot(loop)
    start_uvicorn(loop)
