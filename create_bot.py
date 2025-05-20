import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())

token = os.getenv("TOKEN")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()