from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.st_user_commands import st_User_Commands
from services.constants.callbacks import CommandsCallbacks
from database.orm_query import (orm_get_user_by_id, orm_update_user_balance,
                                orm_add_operation, orm_get_user_by_phone_number)
from database.models import User
from services.constants.operations import Operations
from services.profile_displayer import show_profile
from create_bot import bot

router = Router()

@router.callback_query(F.data == CommandsCallbacks.write_transfer)
async def write_transfer_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Поделитель контактом человека, которому переводили средства")
    await state.set_state(st_User_Commands.st_TransferCommand.phone_number_state)

@router.message(st_User_Commands.st_TransferCommand.phone_number_state, F.contact)
async def find_user_by_contact(message: Message, state: FSMContext, session: AsyncSession):
    phone_number = message.contact.phone_number.replace('+', '')
    user: User = await orm_get_user_by_phone_number(session, phone_number)

    if user is None:
        await message.answer("Такого пользователя не существует")
        await show_profile(message.from_user.id, session)
        await state.clear()
    else:
        await message.answer("Введите комментарий")
        await state.update_data(phone_number=phone_number)
        await state.set_state(st_User_Commands.st_TransferCommand.comment_state)

@router.message(st_User_Commands.st_TransferCommand.comment_state)
async def save_comment(message: Message, state: FSMContext):
    await state.update_data(comment = message.text)
    await message.answer("Введите сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

async def repeat_transfer(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите пожалуйста корректную сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.amount_state)
async def save_transfer(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    comment: str = state_data[st_User_Commands.comment_key]
    income_transfer_user_phone_number = state_data[st_User_Commands.phone_number_key]
    income_transfer_user: User = await orm_get_user_by_phone_number(session, income_transfer_user_phone_number)
    income_transfer_user_balance: float = income_transfer_user.balance

    user: User = await orm_get_user_by_id(session, message.from_user.id)
    balance: float = user.balance

    if message.text.lower() == "inf" or message.text.lower() == "nan":
        await repeat_transfer(message.chat.id, state)
    else:
        if message.text.isdigit():
            amount: float = float(message.text)

            if amount < 0 or (balance - amount) < 0:
                await repeat_transfer(message.chat.id, state)
            else:
                balance -= amount
                income_transfer_user_balance += amount

                await orm_update_user_balance(session, user.id, balance)
                await orm_update_user_balance(session, income_transfer_user.id, balance)

                await orm_add_operation(
                    session=session,
                    user_id=user.id,
                    amount=amount,
                    comment=comment,
                    operation_type=Operations.TRANSFER_TO.value,
                    transfer_user_id=income_transfer_user.id
                )
                await orm_add_operation(
                    session=session,
                    user_id=income_transfer_user.id,
                    amount=amount,
                    comment=comment,
                    operation_type=Operations.TRANSFER_FROM.value,
                    transfer_user_id=user.id
                )

                await message.answer("Перевод успешно записан")
                await show_profile(message.from_user.id, session)
                await state.clear()
        else:
            await repeat_transfer(message.chat.id, state)