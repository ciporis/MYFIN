import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.db import DataBaseSession
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats

from database.engine import create_db, drop_db, session_maker
from create_bot import dp, bot
from handlers.init import setup_handlers
from middlewares.scheduler import SchedulerMiddleware

setup_handlers(dp)

commands = [BotCommand(command="start", description="Старт"),
            BotCommand(command="promocode", description="Промокод")]

import pprint

from create_bot import bot, app, dp, token, web
from middlewares.db import DataBaseSession
from aiogram.types import Update

webhook_path = f"/{token}"

async def set_webhook():
    # webhook_url = f"https://bot.erahotels.ru{webhook_path}"
    webhook_url = f"https://scantily-innocent-cheetah.cloudpub.ru:443{webhook_path}"
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=dp.resolve_used_update_types()
    )


async def on_startup(_):
    scheduler.start()

    drop_parameter = False
    bot.my_admins_list = []
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())

    if drop_parameter:
        await drop_db()

    await create_db()
    await set_webhook()
    print(f"{'-' * 20}START{'-' * 20}")

async def on_shutdown(_):
    if scheduler.running:
        scheduler.shutdown(wait=True)

    print(f"{'-'*20}STOPPED{'-'*20}")

async def handle_webhook(request):
    url = str(request.url)
    index = url.rfind('/')
    url_token = url[index + 1:]
    request_data = await request.json()
    print(request_data)

    if url_token == token:
        # Проверяем, откуда пришел запрос
        if 'update_id' in request_data:
            # Обработка обновления от Telegram
            update = Update(**request_data)
            await dp.feed_webhook_update(bot=bot, update=update)
            return web.Response()
        else:
            return web.Response()

    else:
        return web.Response(status=403)

app.router.add_post(f"/{token}", handle_webhook)

if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    dp.update.middleware(SchedulerMiddleware(scheduler))

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(
        app,
        host="0.0.0.0",
        # port=4000
        port=8080
    )
