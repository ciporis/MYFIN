import asyncio

from middlewares.db import DataBaseSession

from database.engine import create_db, drop_db, session_maker
from create_bot import dp, bot
from handlers.init import setup_handlers

setup_handlers(dp)

async def on_startup(bot):
    drop_parameter = False

    if drop_parameter:
        await drop_db()

    await create_db()
    print(f"{'-' * 20}START{'-' * 20}")


async def on_shutdown(bot):
    print(f"{'-'*20}STOPPED{'-'*20}")

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{'-'*20}STOPPED{'-'*20}")