import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())

token = os.getenv("TOKEN")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def set_bebra():
    await FSMContext.set_dont_delete_on_clear(FSMContext, "current_wallet")

asyncio.run(set_bebra())

dp = Dispatcher()