from aiogram import Router
from handlers import registration
from handlers.user_commands import start, income, outcome, transfer, operations_history, show_wallet, send_excel_report
from handlers import wallet_maker, category_maker, profile_editter, ai_recommendations

from services import profile_displayer

def setup_handlers(dp: Router):
    user_router = Router()

    user_router.include_router(start.router)
    user_router.include_router(registration.router)
    user_router.include_router(income.router)
    user_router.include_router(outcome.router)
    user_router.include_router(transfer.router)
    user_router.include_router(operations_history.router)
    user_router.include_router(wallet_maker.router)
    user_router.include_router(send_excel_report.router)
    user_router.include_router(show_wallet.router)
    user_router.include_router(profile_displayer.router)
    user_router.include_router(category_maker.router)
    user_router.include_router(profile_editter.router)
    user_router.include_router(ai_recommendations.router)

    dp.include_router(user_router)