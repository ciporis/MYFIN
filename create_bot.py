import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiohttp import web

from dotenv import load_dotenv, find_dotenv

from webhooks.premium_operations_history_webhook import premium_operations_history_webhook
from webhooks.qr_code_webhook import qr_code_webhook

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())

token = os.getenv("TOKEN")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
app = web.Application()

app.router.add_post("/Operations", premium_operations_history_webhook)
app.router.add_post(f"/QR", qr_code_webhook)

dp = Dispatcher()