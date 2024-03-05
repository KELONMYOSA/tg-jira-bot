import importlib
import pkgutil

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


def start_bot(loop):
    print("The telegram bot has started!")
    try:
        init_bot()
        while True:
            loop.run_until_complete(bot.polling())
    except Exception as e:
        print(e)
