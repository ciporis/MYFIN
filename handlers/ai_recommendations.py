from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Operation
from database.orm_query import orm_get_all_categories, orm_get_operations_for_period
from keyboards.inline import get_callback_btns
from services import openai
from services.constants.operations import Operations

router = Router()

@router.callback_query(F.data == "get_ai_tips")
async def analyze_profile(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.edit_text("загрузка...")

    today = datetime.today()
    categories = await orm_get_all_categories(session, callback.from_user.id)
    operations = await orm_get_operations_for_period(session, callback.from_user.id, today.day)
    incomes = []
    spends = []

    for operation in operations:
        operation: Operation
        if (operation.operation_type == Operations.INCOME.value or
                operation.operation_type == Operations.TRANSFER_FROM.value):
            incomes.append(operation)
        elif (operation.operation_type == Operations.OUTCOME.value or
              operation.operation_type == Operations.TRANSFER_TO.value):
            spends.append(operation)

    promt = ("Ты - эксперт по определению портрета человека по его тратам, составь небольшой список рекоммендация "
             "по этим данным (сумма траты : категория), не давай много нравоучений, не используй третье лицо, обращайся "
             "на вы ответ не должен быть длиннее 600 символов.\n\n")

    for spend in spends:
        spend: Operation
        promt += f"{spend.amount} : {spend.category}\n"

    ai_response = await openai.generate_text(prompt=promt)

    await callback.message.edit_text(text=ai_response, reply_markup=get_callback_btns(btns={
        "Назад" : "show_profile",
    }))
