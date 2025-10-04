import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Wallet
from database.orm_query import orm_get_user_by_id, orm_get_user_wallets, orm_get_wallet, orm_get_operations_for_period, \
    orm_get_user_wallets, orm_get_wallet_operations_for_current_month, orm_edit_user_current_wallet_id, \
    orm_get_wallet_operations_from_to_as_json
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

    print(f"Current wallet: {user.current_wallet}")

    fio: str = user.fio
    buttons = {}

    current_wallet: Wallet = user.current_wallet

    current_wallet_operations = await orm_get_wallet_operations_for_current_month(session, current_wallet.id)
    incomes_amount = 0
    outcomes_amount = 0

    print(current_wallet.title)
    print(current_wallet.is_hidden)

    for operation in current_wallet_operations:
        if operation.operation_type == Operations.INCOME.value:
            incomes_amount += operation.amount
        elif operation.operation_type == Operations.OUTCOME.value:
            outcomes_amount += operation.amount

    buttons["📥 Доход"] = callbacks.WalletOperations.write_income
    buttons["📤 Расход"] = callbacks.WalletOperations.write_outcome
    buttons["🔄 Перевод"] = callbacks.WalletOperations.write_transfer
    buttons["🧾 Чек"] = "piski"
    buttons["📈 Статистика"] = "siski"
    buttons["💳 Счета"] = callbacks.show_wallets
    buttons["⚙️ Настройки"] = callbacks.settings


    if user.is_subscribed:
        sizes = (2, 2, 1, 2)
    else:
        sizes = (2, 2, 1)
        buttons["📈 Статистика"] = callbacks.WalletOperations.show_operations_history
        del buttons["🧾 Чек"]
        del buttons["💳 Счета"]


    if current_wallet.is_hidden is True:
        text = f"""
Здравствуйте, {fio}! 👋

{current_wallet.title} 💼

Баланс: <tg-spoiler>{current_wallet.amount}</tg-spoiler> руб 💰

За текущий месяц:
├ Доход: <tg-spoiler>{incomes_amount}</tg-spoiler> руб 📈
└ Расход: <tg-spoiler>{outcomes_amount}</tg-spoiler> руб 📉
"""
    else:
        text = f"""
Здравствуйте, {fio}! 👋

{current_wallet.title} 💼

Баланс: {current_wallet.amount} руб 💰

За текущий месяц:
├ Доход: {incomes_amount} руб 📈
└ Расход: {outcomes_amount} руб 📉
"""

    await callback.message.edit_text(text = text, reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes,
    ))

async def show_profile(user_id: int, session: AsyncSession, state: FSMContext):
    user: User = await orm_get_user_by_id(session, user_id)

    print(f"Current wallet: {user.current_wallet}")

    fio: str = user.fio
    buttons = {}

    wallets = await orm_get_user_wallets(session, user_id)

    if user.current_wallet is None:
        current_wallet: Wallet = wallets[0]
        await orm_edit_user_current_wallet_id(session, user.id, current_wallet.id)
    else:
        current_wallet = user.current_wallet

    print(await orm_get_wallet_operations_from_to_as_json(session, current_wallet.id,
                                                          datetime.date.today() - datetime.timedelta(days=30),
                                                          datetime.date.today()))

    print(current_wallet.title)
    print(current_wallet.is_hidden)

    current_wallet_operations = await orm_get_wallet_operations_for_current_month(session, current_wallet.id)
    incomes_amount = 0
    outcomes_amount = 0

    for operation in current_wallet_operations:
        if operation.operation_type == Operations.INCOME.value:
            incomes_amount += operation.amount
        elif operation.operation_type == Operations.OUTCOME.value:
            outcomes_amount += operation.amount

    buttons["📥 Доход"] = callbacks.WalletOperations.write_income
    buttons["📤 Расход"] = callbacks.WalletOperations.write_outcome
    buttons["🔄 Перевод"] = callbacks.WalletOperations.write_transfer
    buttons["🧾 Чек"] = "piski"
    buttons["📈 Статистика"] = "siski"
    buttons["💳 Счета"] = callbacks.show_wallets
    buttons["⚙️ Настройки"] = callbacks.settings

    if user.is_subscribed:
        sizes = (2, 2, 1, 2)
    else:
        sizes = (2, 2, 1)
        buttons["📈 Статистика"] = callbacks.WalletOperations.show_operations_history
        del buttons["🧾 Чек"]
        del buttons["💳 Счета"]

    if current_wallet.is_hidden is True:
        text = f"""
Здравствуйте, {fio}! 👋

{current_wallet.title} 💼

Баланс: <tg-spoiler>{current_wallet.amount}</tg-spoiler> руб 💰

За текущий месяц:
├ Доход: <tg-spoiler>{incomes_amount}</tg-spoiler> руб 📈
└ Расход: <tg-spoiler>{outcomes_amount}</tg-spoiler> руб 📉
"""
    else:
        text = f"""
Здравствуйте, {fio}! 👋

{current_wallet.title} 💼

Баланс: {current_wallet.amount} руб 💰

За текущий месяц:
├ Доход: {incomes_amount} руб 📈
└ Расход: {outcomes_amount} руб 📉
"""


    await bot.send_message(chat_id=user_id, text=text, reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))