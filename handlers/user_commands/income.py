from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.st_user_commands import st_User_Commands
from services.constants.callbacks import CommandsCallbacks
from database.orm_query import (orm_get_user_by_id, orm_update_user_balance,
                                orm_add_operation)
from database.models import User
from services.constants.operations import Operations
from services.profile_displayer import show_profile
from create_bot import bot

router = Router()

@router.callback_query(F.data == CommandsCallbacks.write_income)
async def write_income(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите комментарий")
    await state.set_state(st_User_Commands.st_IncomeCommand.comment_state)

@router.message(st_User_Commands.st_IncomeCommand.comment_state)
async def save_comment(message: Message, state: FSMContext):
    await state.update_data(comment = message.text)
    await message.answer("Введите сумму")
    await state.set_state(st_User_Commands.st_IncomeCommand.amount_state)

async def repeat_income(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите пожалуйста корректную сумму")
    await state.set_state(st_User_Commands.st_IncomeCommand.amount_state)

@router.message(st_User_Commands.st_IncomeCommand.amount_state)
async def save_income(message: Message, state: FSMContext, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, message.from_user.id)
    balance: float = user.balance
    state_data = await state.get_data()

    if message.text.isdigit():
        amount: float = float(message.text)

        if amount < 0:
            await repeat_income(message.chat.id, state)
            await state.clear()
        else:
            balance += amount

            await orm_update_user_balance(session, message.from_user.id, balance)

            await orm_add_operation(
                session=session,
                user_id=message.from_user.id,
                amount=amount,
                comment=state_data[st_User_Commands.comment_key],
                operation_type=Operations.INCOME.value,
                transfer_user_id=0
            )
            await message.answer("Успешно!")
            await show_profile(message.from_user.id, session)
            await state.clear()
    else:
        await repeat_income(message.chat.id, state)