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
from services.profile_displayer import show_profile
from create_bot import bot
from keyboards.inline import get_callback_btns

router = Router()

# @router.callback_query(F.data.contains(WalletOperations.write_income))
# async def write_income(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     wallet_id: int = int(callback.data.split('_')[-1])
#     await state.update_data(wallet_id=wallet_id)
#     await callback.answer()

    # categories = await orm_get_all_categories(session, callback.from_user.id)

    # if categories:
    #     for category in categories:
    #         buttons[category.title] = f"select_category_for_income_{category.id}"
    #
    #     buttons["Добавить"] = ProfileCommands.add_category
    #
    #     await callback.message.edit_text("Выберите категорию", reply_markup=get_callback_btns(
    #         btns=buttons,
    #     ))
    # else:
    #     buttons["Добавить"] = ProfileCommands.add_category
    #
    #     await callback.message.edit_text("Выберите категорию", reply_markup=get_callback_btns(
    #         btns=buttons,
    #     ))


@router.callback_query(F.data.contains(WalletOperations.write_income))
async def write_income(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    wallet_id: int = int(callback.data.split('_')[-2])
    page: int = int(callback.data.split('_')[-1])

    await state.update_data(wallet_id=wallet_id, page=page)
    await callback.answer()
    # category_id = int(callback.data.split('_')[-1])
    # await state.update_data(category_id=category_id)
    await callback.message.edit_text("Введите сумму")
    await state.set_state(st_User_Commands.st_IncomeCommand.amount_state)

# async def repeat_income(chat_id: int, state: FSMContext):
#     await bot.send_message(chat_id, "Введите пожалуйста корректную сумму")
#     await state.set_state(st_User_Commands.st_IncomeCommand.amount_state)

@router.message(st_User_Commands.st_IncomeCommand.amount_state)
async def save_amount(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet: Wallet = await orm_get_wallet(session, state_data["wallet_id"])
    page = state_data["page"]
    balance: float = wallet.amount

    if message.text.isdigit():
        amount: float = float(message.text)

        if amount < 0:
            await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                btns={"Назад": f"wallets_page_{page}"}
            ))
            await state.clear()
        else:
            balance += amount
            await state.update_data(amount=amount)
            await message.answer("Комментарий")
            await state.set_state(st_User_Commands.st_IncomeCommand.comment_state)
    else:
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": f"wallets_page_{page}"}
        ))
        await state.clear()

@router.message(st_User_Commands.st_IncomeCommand.comment_state)
async def save_comment(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(comment = message.text)
    await save_operation(message, state, session)

async def save_operation(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet: Wallet = await orm_get_wallet(session, state_data["wallet_id"])
    page = state_data["page"]

    # category_id = state_data["category_id"]
    amount = state_data["amount"]
    comment = state_data["comment"]
    # category: Category = await orm_get_category(session, category_id)

    await orm_edit_wallet_amount(session, wallet.id, wallet.amount + amount)

    await orm_add_operation(
        session=session,
        user_id=message.from_user.id,
        wallet_id=wallet.id,
        amount=amount,
        comment=comment,
        operation_type=Operations.INCOME.value,
        transfer_user_id=0,
        transfer_wallet_id=0,
        category=""
    )
    await message.answer("Успешно!", reply_markup=get_callback_btns(
        btns={
            "Назад" : f"wallets_page_{page}",
        }
    ))

    await state.clear()