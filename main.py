import asyncio

import uvicorn

from src.bot.app import start_bot
from src.webhook.app import app


def start_uvicorn(loop):
    host = "0.0.0.0"
    port = 5555
    config = uvicorn.Config(app, host=host, port=port, loop=loop)
    server = uvicorn.Server(config)
    loop.create_task(server.serve())


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_uvicorn(loop)
    start_bot(loop)
