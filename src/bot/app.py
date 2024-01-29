import asyncio
import importlib
import pkgutil

from telebot.apihelper import ApiTelegramException
from telebot.async_telebot import AsyncTeleBot

from src.bot import handlers
from src.config import settings

bot = AsyncTeleBot(settings.BOT_TOKEN)


def init_bot():
    try:
        for x in pkgutil.iter_modules(handlers.__path__):
            handler = importlib.import_module("src.bot.handlers." + x.name)
            handler.run(bot)
    except Exception as e:
        print(e)


async def start_bot():
    print("The telegram bot has started!")
    while True:
        try:
            await bot.polling()
        except ApiTelegramException as e:
            if e.error_code == 429:
                print(f"Received error 429: {e}")
                await asyncio.sleep(5)
            else:
                print(f"Unhandled exception: {e}")
                await asyncio.sleep(1)
