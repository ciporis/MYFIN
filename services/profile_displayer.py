from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Wallet
from database.orm_query import orm_get_user_by_id, orm_get_wallets, orm_get_wallet, orm_get_operations_for_period, \
    orm_get_wallets, orm_get_wallet_operations_for_period
from services.constants.callbacks import WalletOperations, ProfileCommands
from services.constants import callbacks
from create_bot import bot
from keyboards.inline import get_callback_btns
from services.constants.operations import Operations

router = Router()

@router.callback_query(F.data == ProfileCommands.show_profile)
async def handle_show_profile_callback(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    fio: str = user.fio
    buttons = {}
    wallets = await orm_get_wallets(session, user.id)

    current_wallet = None

    for wallet in wallets:
        current_wallet: Wallet = wallet
        await state.update_data(current_wallet=current_wallet)
        break

    current_wallet_operations = await orm_get_wallet_operations_for_period(session, callback.from_user.id, 30)
    incomes_amount = 0
    outcomes_amount = 0

    for operation in current_wallet_operations:
        if operation.operation_type == Operations.INCOME.value:
            incomes_amount += operation.amount
        elif operation.operation_type == Operations.OUTCOME.value:
            outcomes_amount += operation.amount

    buttons["Доход"] = callbacks.WalletOperations.write_income
    buttons["Расход"] = callbacks.WalletOperations.write_outcome
    buttons["Перевод"] = callbacks.WalletOperations.write_transfer
    buttons["Добавить чек"] = callbacks.WalletOperations.write_income
    buttons["Статистика"] = callbacks.WalletOperations.write_income
    buttons["Выбрать счёт"] = callbacks.WalletOperations.write_income
    buttons["Настройки"] = callbacks.settings

    sizes = (2, 2, 1)

    if user.is_subscribed:
        sizes = (2, 2, 1, 2)
    else:
        sizes = (2, 2, 1, 1)
        del buttons["Выбрать счёт"]

    text = f"""
            Здравствуйте, {fio}!

            {current_wallet.title}

    Баланс: {current_wallet.amount} руб

    За текущий месяц:
    Доход: {incomes_amount} руб
    Расход: {outcomes_amount} руб
    """

    await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))

async def show_profile(user_id: int, session: AsyncSession, state: FSMContext):
    user: User = await orm_get_user_by_id(session, user_id)
    fio: str = user.fio
    buttons = {}

    wallets = await orm_get_wallets(session, user.id)
    current_wallet = None

    for wallet in wallets:
        current_wallet: Wallet = wallet
        await state.update_data(current_wallet=current_wallet)
        break

    current_wallet_operations = await orm_get_wallet_operations_for_period(session, user_id, 30)
    incomes_amount = 0
    outcomes_amount = 0

    for operation in current_wallet_operations:
        if operation.operation_type == Operations.INCOME.value:
            incomes_amount += operation.amount
        elif operation.operation_type == Operations.OUTCOME.value:
            outcomes_amount += operation.amount

    buttons["Доход"] = callbacks.WalletOperations.write_income
    buttons["Расход"] = callbacks.WalletOperations.write_outcome
    buttons["Перевод"] = callbacks.WalletOperations.write_transfer
    buttons["Добавить чек"] = callbacks.WalletOperations.write_income
    buttons["Статистика"] = callbacks.WalletOperations.write_income
    buttons["Выбрать счёт"] = callbacks.WalletOperations.write_income
    buttons["Настройки"] = callbacks.settings

    if user.is_subscribed:
        sizes = (2, 2, 1, 2)
    else:
        sizes = (2, 2, 1, 1)
        del buttons["Выбрать счёт"]

    text = f"""
            Здравствуйте, {fio}!
    
            {current_wallet.title}
    
    Баланс: {current_wallet.amount} руб
    
    За текущий месяц:
    Доход: {incomes_amount} руб
    Расход: {outcomes_amount} руб
    """

    await bot.send_message(chat_id=user_id, text=text, reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))