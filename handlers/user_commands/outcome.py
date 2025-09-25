from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.st_user_commands import st_User_Commands
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import (orm_add_operation, orm_get_wallet,
                                orm_edit_wallet_amount, orm_get_all_categories, orm_get_category)
from database.models import Wallet, Category
from services.constants.operations import Operations
from services.constants import callbacks
from keyboards.inline import get_callback_btns
from services import openai

router = Router()

categories = [
    "Продукты питания",
    "Транспорт Жилье",
    "Кафе и рестораны",
    "Здоровье",
    "Одежда и обувь",
    "Развлечения",
    "Связь",
    "Личные расходы",
    "Накопления и инвестиции",
    "Прочее"
]

@router.callback_query(F.data.contains(WalletOperations.write_outcome))
async def write_outcome(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet = state_data["current_wallet"]

    if wallet.amount == 0:
        await callback.answer("У вас недостаточно средств", show_alert=True)
        return

    await callback.answer()

    await callback.message.edit_text("Введите сумму")
    await state.set_state(st_User_Commands.st_OutcomeCommand.amount_state)

@router.message(st_User_Commands.st_OutcomeCommand.amount_state)
async def save_amount(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet: Wallet = state_data["current_wallet"]
    balance: float = wallet.amount

    if message.text.isdigit():
        amount: float = float(message.text)

        if amount < 0 or wallet.amount - amount < 0:
            await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                btns={"Назад" : callbacks.WalletOperations.write_income},
            ))
            await state.clear()
        else:
            balance += amount
            await state.update_data(amount=amount)
            await message.answer("Комментарий")
            await state.set_state(st_User_Commands.st_OutcomeCommand.comment_state)
    else:
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": callbacks.ProfileCommands.show_profile}
        ))
        await state.clear()

@router.message(st_User_Commands.st_OutcomeCommand.comment_state)
async def save_comment(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(comment = message.text)
    await save_operation(message, state, session)

async def save_operation(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet: Wallet = state_data["current_wallet"]

    amount = state_data["amount"]
    comment = state_data["comment"]

    categories_text = ""

    for category in categories:
        categories_text += f"\n{category}\n"

    promt = (f"Определи по комментарию к расходу категорию, к которой он пренадлежит. В ответе напиши только название категори\n"
             f"Комментарий: {comment}\n"
             f"Категории: {categories_text}")

    await message.answer("Определяю категорию расхода...")

    determined_category = await openai.generate_text(promt)

    await message.answer(f"Категория для вашего расхода - {determined_category}")

    await orm_edit_wallet_amount(session, wallet.id, wallet.amount - amount)

    await orm_add_operation(
        session=session,
        user_id=message.from_user.id,
        wallet_id=wallet.id,
        amount=amount,
        comment=comment,
        operation_type=Operations.OUTCOME.value,
        receiver="",
        category=determined_category
    )

    await message.answer("Успешно!", reply_markup=get_callback_btns(
        btns={
            "Назад": callbacks.ProfileCommands.show_profile,
        }
    ))
    await state.clear()