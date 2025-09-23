from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from openpyxl import Workbook
import io

from database.orm_query import (orm_get_user_by_id, orm_get_wallet,
                                orm_get_all_operations)
from database.models import User, Wallet
from create_bot import bot

router = Router()

@router.callback_query(F.data == "send_xlsx")
async def send_xlsx(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Report"
    headers = ["Дата", "Сумма", "Тип", "Комментарий", "Кошелёк", "Другой пользователь"]
    worksheet.append(headers)

    operations = await orm_get_all_operations(session, callback.from_user.id)

    for operation in operations:
        wallet: Wallet = await orm_get_wallet(session, operation.wallet_id)
        transfer_user_name = '-'
        if operation.transfer_user_id != 0:
            transfer_user: User = await orm_get_user_by_id(session, operation.transfer_user_id)
            transfer_user_name = transfer_user.fio

        row = [f"{operation.created.day}.{operation.created.month}.{operation.created.year}", operation.amount, operation.operation_type,
               operation.comment, wallet.title, transfer_user_name]

        worksheet.append(row)

    excel_buffer = io.BytesIO()
    workbook.save(excel_buffer)
    excel_buffer.seek(0)

    await bot.send_document(chat_id=callback.from_user.id,
                            document=BufferedInputFile(
                                file=excel_buffer.getvalue(),
                                filename="report.xlsx",
                            ),
                            caption="Ваша отчетность"
    )