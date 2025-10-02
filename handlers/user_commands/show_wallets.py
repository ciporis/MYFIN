from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from openai.types.beta.thread_create_params import Message

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Wallet
from database.orm_query import orm_get_user_by_id, orm_get_user_wallets, orm_get_wallet, orm_get_operations_for_period, \
    orm_get_user_wallets, orm_get_wallet_operations_for_current_month, orm_edit_user_current_wallet_id
from services.constants.callbacks import WalletOperations, ProfileCommands
from services.constants import callbacks
from create_bot import bot
from keyboards.inline import get_callback_btns
from services.constants.operations import Operations

router = Router()

@router.callback_query(F.data == callbacks.show_wallets)
async def show_wallets(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    current_wallet: Wallet = user.current_wallet

    wallets = await orm_get_user_wallets(session, callback.from_user.id)

    buttons = {}

    for wallet in wallets:
        wallet: Wallet

        if wallet.id == current_wallet.id:
            buttons[f"{wallet.title} ✅"] = f"make_wallet_default_{wallet.id}"
        else:
            buttons[wallet.title] = f"make_wallet_default_{wallet.id}"

    buttons["Добавить"] = WalletOperations.add_wallet
    buttons["Назад"] = ProfileCommands.show_profile

    await callback.message.edit_text(text="Счета:", reply_markup=get_callback_btns(
        btns=buttons
    ))

@router.callback_query(F.data.startswith("make_wallet_default_"))
async def make_wallet_default(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()

    wallet_id = int(callback.data.split("_")[-1])

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    current_wallet: Wallet = user.current_wallet

    if wallet_id == current_wallet.id:
        await callback.answer(text="Этот счёт уже выбран по умолчанию", show_alert=True)
        return

    new_current_wallet: Wallet = await orm_get_wallet(session, wallet_id)

    await orm_edit_user_current_wallet_id(session, user.id, new_current_wallet.id)

    wallets = await orm_get_user_wallets(session, callback.from_user.id)

    buttons = {}

    for wallet in wallets:
        wallet: Wallet

        if wallet.id == new_current_wallet.id:
            buttons[f"{wallet.title} ✅"] = f"make_wallet_default_{wallet.id}"
        else:
            buttons[wallet.title] = f"make_wallet_default_{wallet.id}"

    buttons["Добавить ➕"] = WalletOperations.add_wallet
    buttons["Назад"] = ProfileCommands.show_profile

    await callback.message.edit_text(text="Счета:", reply_markup=get_callback_btns(
        btns=buttons
    ))
