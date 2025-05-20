from aiogram import Router
from handlers import registration
from handlers.user_commands import start, income, outcome, transfer, operations_history

def setup_handlers(dp: Router):
    user_router = Router()

    user_router.include_router(start.router)
    user_router.include_router(registration.router)
    user_router.include_router(income.router)
    user_router.include_router(outcome.router)
    user_router.include_router(transfer.router)
    user_router.include_router(operations_history.router)

    dp.include_router(user_router)