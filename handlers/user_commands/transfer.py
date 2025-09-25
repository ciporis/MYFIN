from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import get_callback_btns
from keyboards.reply import get_phone_number_keyboard
from states.st_user_commands import st_User_Commands
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import (orm_get_user_by_id,
                                orm_add_operation, orm_get_user_by_phone_number, orm_get_all_categories, orm_get_wallet,
                                orm_get_category, orm_edit_wallet_amount, orm_get_wallets)
from database.models import User, Wallet, Category
from services.constants.operations import Operations
from services.constants.callbacks import ProfileCommands
from services.profile_displayer import show_profile
from states import st_user_commands
from create_bot import bot

router = Router()

@router.callback_query(F.data.contains(WalletOperations.write_transfer))
async def write_transfer_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet: Wallet = state_data["current_wallet"]

    if wallet.amount == 0:
        await callback.answer("У вас недостаточно средств", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(text="Отправьте имя получателя или контакт, из которого нужно взять имя")
    await state.set_state(st_User_Commands.st_TransferCommand.name_state)

@router.message(st_User_Commands.st_TransferCommand.name_state, F.contact)
async def get_user_name_by_contact(message: Message, state: FSMContext, session: AsyncSession):
    name = message.contact.first_name

    await state.update_data(name=name)
    await message.answer("Введиет сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.name_state, F.text)
async def set_user_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введиет сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.amount_state)
async def save_transfer_amount(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    wallet: Wallet = state_data["current_wallet"]
    balance: float = wallet.amount

    if message.text.lower() == "inf" or message.text.lower() == "nan":
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": ProfileCommands.show_profile}
        ))
        await state.clear()
    else:
        if message.text.isdigit():
            amount: float = float(message.text)

            if amount < 0 or (balance - amount) < 0:
                await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                    btns={"Назад": ProfileCommands.show_profile}
                ))
                await state.clear()
            else:
                await state.update_data(amount=amount)
                await save_operation(message.from_user.id, state, session)
        else:
            await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                btns={"Назад": ProfileCommands.show_profile}
            ))
            await state.clear()

async def save_operation(user_id, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    wallet: Wallet = state_data["current_wallet"]

    receiver: str = state_data["name"]
    amount: float = state_data["amount"]

    user: User = await orm_get_user_by_id(session, user_id)

    await orm_add_operation(
        session=session,
        user_id=user.id,
        wallet_id=wallet.id,
        amount=amount,
        comment="",
        operation_type=Operations.TRANSFER_TO.value,
        receiver=receiver,
        category="",
    )
    await orm_edit_wallet_amount(session, wallet.id, wallet.amount - amount)

    await bot.send_message(user_id, "Успешно!", reply_markup=get_callback_btns(
        btns={
            "Назад": ProfileCommands.show_profile,
        }
    ))
    await state.clear()