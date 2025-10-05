from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import get_callback_btns
from keyboards.reply import get_phone_number_keyboard
from services.constants import callbacks
from services.validation import is_float
from states.st_user_commands import st_User_Commands
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import (orm_get_user_by_id,
                                orm_add_operation, orm_get_user_by_phone_number, orm_get_all_categories, orm_get_wallet,
                                orm_get_category, orm_edit_wallet_amount, orm_get_user_wallets, orm_get_receivers,
                                orm_get_receiver, orm_add_receiver)
from database.models import User, Wallet, Category, Receiver
from services.constants.operations import Operations
from services.constants.callbacks import ProfileCommands
from services.profile_displayer import show_profile
from states import st_user_commands
from create_bot import bot

router = Router()

@router.callback_query(F.data.contains(WalletOperations.write_transfer))
async def write_transfer_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    wallet: Wallet = user.current_wallet

    if wallet.amount <= 0:
        await callback.answer("У вас недостаточно средств", show_alert=True)
        return

    text = "Отправьте имя получателя или контакт, из которого нужно взять имя"

    receivers = await orm_get_receivers(session, callback.from_user.id)

    if receivers:
        text += "\nИли выберите из предложенных"

        buttons = {}

        for receiver in receivers:
            receiver: Receiver

            buttons[receiver.name] = f"set_receiver_{receiver.id}"

        buttons["Назад"] = callbacks.ProfileCommands.show_profile

        await callback.message.edit_text(text=text, reply_markup=get_callback_btns(
            btns=buttons
        ))
    else:
        await callback.message.edit_text(text=text, reply_markup=get_callback_btns(
            btns={
                "Назад" : callbacks.ProfileCommands.show_profile,
            }
        ))

    await state.set_state(st_User_Commands.st_TransferCommand.name_state)

@router.callback_query(st_User_Commands.st_TransferCommand.name_state, F.data.not_contains(callbacks.ProfileCommands.show_profile))
async def save_receiver_name(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    receiver_id = int(callback.data.split("_")[-1])
    receiver: Receiver = await orm_get_receiver(session, receiver_id)

    await state.update_data(name=receiver.name)
    await callback.message.edit_text("Введите сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.name_state, F.contact)
async def get_user_name_by_contact(message: Message, state: FSMContext, session: AsyncSession):
    name = message.contact.first_name

    await state.update_data(name=name)

    receivers = await orm_get_receivers(session, message.from_user.id)
    receivers_names = [receiver.name for receiver in receivers]

    if name not in receivers_names:
        await orm_add_receiver(session, message.from_user.id, name)

    await message.answer("Введите сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.name_state, F.text)
async def set_user_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(name=message.text)

    receivers = await orm_get_receivers(session, message.from_user.id)
    receivers_names = [receiver.name for receiver in receivers]

    if message.text not in receivers_names:
        await orm_add_receiver(session, message.from_user.id, message.text)

    await message.answer("Введите сумму")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.amount_state)
async def save_transfer_amount(message: Message, state: FSMContext, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, message.from_user.id)
    wallet: Wallet = user.current_wallet
    balance: float = wallet.amount

    if message.text.lower() == "inf" or message.text.lower() == "nan":
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": ProfileCommands.show_profile}
        ))
        await state.clear()
    else:
        if is_float(message.text):
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

    user: User = await orm_get_user_by_id(session, user_id)
    wallet: Wallet = user.current_wallet

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