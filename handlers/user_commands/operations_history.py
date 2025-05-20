from datetime import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from services.constants.callbacks import CommandsCallbacks
from services.profile_displayer import show_profile
from database.orm_query import orm_get_all_operations
from keyboards.inline import get_callback_btns

router = Router()

@router.callback_query(F.data == "menu")
async def show_profile_callback(call: CallbackQuery, session: AsyncSession):
    await call.message.delete()
    await show_profile(call.from_user.id, session)

@router.callback_query(F.data == CommandsCallbacks.show_operations_history)
async def show_operations_history(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()

    text = "Дата | Тип операции | Сумма\n"

    operations = await orm_get_all_operations(session, callback.from_user.id)
    print(operations)
    print(type(operations))
    if operations:
        for operation in operations:
            date: datetime = operation.created
            amount: float = operation.amount
            operation_type: str = operation.operation_type

            line = f"{date.day}.{date.month}.{date.year} | {operation_type} | {amount} руб.\n"
            text += line

        await callback.message.edit_text(text, reply_markup=get_callback_btns(btns={
            "Назад": "menu"
        }))
    else:
        await callback.message.answer("История пуста", show_alert=True)