from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import overload

from services.constants import callbacks
from states.st_user_commands import st_User_Commands
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import (orm_add_operation, orm_get_wallet,
                                orm_edit_wallet_amount, orm_get_all_categories, orm_get_category, orm_get_user_by_id)
from database.models import Wallet, Category, User
from services.constants.operations import Operations
from services.constants.callbacks import ProfileCommands
from keyboards.inline import get_callback_btns

router = Router()

@router.callback_query(F.data.contains(WalletOperations.write_income))
async def write_income(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите сумму", reply_markup=get_callback_btns(
        btns={
            "Назад" : callbacks.ProfileCommands.show_profile,
        }
    ))
    await state.set_state(st_User_Commands.st_IncomeCommand.amount_state)

@router.message(st_User_Commands.st_IncomeCommand.amount_state)
async def save_amount(message: Message, state: FSMContext, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, message.from_user.id)
    wallet: Wallet = user.current_wallet
    balance: float = wallet.amount

    if message.text.isdigit():
        amount: float = float(message.text)

        if amount < 0:
            await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                btns={"Назад": ProfileCommands.show_profile}
            ))
            await state.clear()
        else:
            balance += amount
            await state.update_data(amount=amount)
            await message.answer("Комментарий")
            await state.set_state(st_User_Commands.st_IncomeCommand.comment_state)
    else:
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": ProfileCommands.show_profile}
        ))
        await state.clear()

@router.message(st_User_Commands.st_IncomeCommand.comment_state)
async def save_comment(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(comment = message.text)
    await save_operation(message, state, session)

async def save_operation(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    user: User = await orm_get_user_by_id(session, message.from_user.id)
    wallet: Wallet = user.current_wallet

    amount = state_data["amount"]
    comment = state_data["comment"]

    await orm_edit_wallet_amount(session, wallet.id, wallet.amount + amount)

    await orm_add_operation(
        session=session,
        user_id=message.from_user.id,
        wallet_id=wallet.id,
        amount=amount,
        comment=comment,
        operation_type=Operations.INCOME.value,
        receiver="",
        category=""
    )
    await message.answer("Успешно!", reply_markup=get_callback_btns(
        btns={
            "Назад" : ProfileCommands.show_profile,
        }
    ))

    await state.clear()