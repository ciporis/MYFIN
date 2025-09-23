from aiogram import Router, F
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Wallet
from database.orm_query import orm_get_user_by_id, orm_get_wallets
from services.constants.callbacks import WalletOperations, ProfileCommands
from create_bot import bot
from keyboards.inline import get_callback_btns

router = Router()

@router.callback_query(F.data == ProfileCommands.show_profile)
async def handle_show_profile_callback(callback: CallbackQuery, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    fio: str = user.fio
    buttons = {}
    wallets = await orm_get_wallets(session, user.id)

    buttons["Кошельки"] = f"wallets_page_1"
    buttons["Отчетность в EXCEL"] = "send_xlsx"
    buttons["Получить рекоммендации от нейросети"] = "get_ai_tips"
    buttons["Настройки профиля"] = "edit_profile"

    await callback.message.edit_text(text=fio, reply_markup=get_callback_btns(
        btns=buttons,
    ))

async def show_profile(user_id: int, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, user_id)
    fio: str = user.fio
    buttons = {}

    first_wallet: Wallet = await orm_

    buttons["Кошельки"] = f"wallets_page_1"
    buttons["Отчетность в EXCEL"] = "send_xlsx"
    buttons["Получить рекоммендации от нейросети"] = "get_ai_tips"
    buttons["Настройки профиля"] = "edit_profile"

    text = f"""
    Здравствуйте, {fio}!
    
    Ваш текущий счёт - ...
    
    
    
    """

    await bot.send_message(chat_id=user_id, text=f"{fio}", reply_markup=get_callback_btns(
        btns=buttons,
    ))