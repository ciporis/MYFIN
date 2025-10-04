from aiogram import Router
from handlers import registration
from handlers.user_commands import (start, income, outcome, transfer, operations_history, show_wallet, send_excel_report,
                                    show_wallets)
from handlers import wallet_maker, settings, ai_recommendations, voice_handler, user_group, user_private, premium
from handlers.admin import admin_private

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
    user_router.include_router(settings.router)
    user_router.include_router(ai_recommendations.router)
    user_router.include_router(voice_handler.router)
    user_router.include_router(show_wallets.router)
    user_router.include_router(user_group.router)
    user_router.include_router(admin_private.router)
    user_router.include_router(user_private.router)
    user_router.include_router(premium.router)

    dp.include_router(user_router)