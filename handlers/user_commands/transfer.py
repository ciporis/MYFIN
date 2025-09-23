from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import get_callback_btns
from states.st_user_commands import st_User_Commands
from services.constants.callbacks import WalletOperations, ProfileCommands
from database.orm_query import (orm_get_user_by_id,
                                orm_add_operation, orm_get_user_by_phone_number, orm_get_all_categories, orm_get_wallet,
                                orm_get_category, orm_edit_wallet_amount, orm_get_wallets)
from database.models import User, Wallet, Category
from services.constants.operations import Operations
from services.profile_displayer import show_profile
from create_bot import bot

router = Router()

@router.callback_query(F.data.contains(WalletOperations.write_transfer))
async def write_transfer_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    wallet_id = int(callback.data.split('_')[-2])
    page = int(callback.data.split('_')[-1])

    wallet = await orm_get_wallet(session, wallet_id)
    if wallet.amount == 0:
        await callback.answer("У вас недостаточно средств", show_alert=True)
        return

    await state.update_data(wallet_id=wallet_id, page=page)

    await callback.answer()
    await callback.message.answer(text="Поделитель контактом человека, которому переводили средства")
    await state.set_state(st_User_Commands.st_TransferCommand.phone_number_state)

@router.message(st_User_Commands.st_TransferCommand.phone_number_state, F.contact)
async def find_user_by_contact(message: Message, state: FSMContext, session: AsyncSession):
    phone_number = message.contact.phone_number.replace('+', '')
    user: User = await orm_get_user_by_phone_number(session, phone_number)

    # categories = await orm_get_all_categories(session, message.from_user.id)
    # buttons = {}

    if user is None:
        await message.answer("Такого пользователя не существует")
        await show_profile(message.from_user.id, session)
        await state.clear()
    else:
        # if categories:
        #     for category in categories:
        #         buttons[category.title] = f"select_category_for_transfer_{category.id}"
        #
        #     buttons["Добавить"] = ProfileCommands.add_category
        #
        #     await message.answer("Выберите категорию", reply_markup=get_callback_btns(
        #         btns=buttons,
        #     ))
        # else:
        #     buttons["Добавить"] = ProfileCommands.add_category
        #
        #     await message.answer("Выберите категорию", reply_markup=get_callback_btns(
        #         btns=buttons,
        #     ))
        await state.update_data(phone_number=phone_number)
        await choose_wallet(message, state, session)

# @router.callback_query(F.data.contains("select_category_for_transfer"))
async def choose_wallet(message: Message, state: FSMContext, session: AsyncSession):
    # category_id = int(callback.data.split('_')[-1])
    # await state.update_data(category_id=category_id)

    state_data = await state.get_data()
    transfer_user: User = await orm_get_user_by_phone_number(session, state_data["phone_number"])
    transfer_user_id: int = transfer_user.id

    wallets = await orm_get_wallets(session, transfer_user_id)

    buttons = {}

    for wallet in wallets:
        buttons[wallet.title] = f"select_wallet_for_transfer_{wallet.id}"

    await bot.send_message(message.from_user.id , "Выберите кошелек пользователя", reply_markup=get_callback_btns(
        btns=buttons
    ))

@router.callback_query(F.data.contains("select_wallet_for_transfer"))
async def save_selected_wallet(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    transfer_wallet_id = int(callback.data.split('_')[-1])
    await callback.answer()
    await state.update_data(transfer_wallet_id=transfer_wallet_id)
    await callback.message.answer("Сумма")
    await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

# async def repeat_transfer(chat_id: int, state: FSMContext):
#     await bot.send_message(chat_id, "Введите пожалуйста корректную сумму")
#     await state.set_state(st_User_Commands.st_TransferCommand.amount_state)

@router.message(st_User_Commands.st_TransferCommand.amount_state)
async def save_transfer_amount(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet_id: int = state_data["wallet_id"]
    page = state_data["page"]

    wallet: Wallet = await orm_get_wallet(session, wallet_id)
    balance: float = wallet.amount

    if message.text.lower() == "inf" or message.text.lower() == "nan":
        await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
            btns={"Назад": f"wallets_page_{page}"}
        ))
        await state.clear()
    else:
        if message.text.isdigit():
            amount: float = float(message.text)

            if amount < 0 or (balance - amount) < 0:
                await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                    btns={"Назад": f"wallets_page_{page}"}
                ))
                await state.clear()
            else:
                await state.update_data(amount=amount)
                await message.answer("Комментарий")
                await state.set_state(st_User_Commands.st_TransferCommand.comment_state)
        else:
            await message.answer("Неккоректный ввод", reply_markup=get_callback_btns(
                btns={"Назад": f"wallets_page_{page}"}
            ))
            await state.clear()

@router.message(st_User_Commands.st_TransferCommand.comment_state)
async def save_comment(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(comment = message.text)
    await save_operation(message, state, session)

async def save_operation(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()

    page = state_data["page"]

    comment: str = state_data["comment"]
    transfer_user_phone_number: str = state_data["phone_number"]
    amount: float = state_data["amount"]
    wallet_id: int = state_data["wallet_id"]
    transfer_wallet_id: int = state_data["transfer_wallet_id"]
    # category_id: int = state_data["category_id"]

    user: User = await orm_get_user_by_id(session, message.from_user.id)
    transfer_user: User = await orm_get_user_by_phone_number(session, transfer_user_phone_number)
    # category: Category = await orm_get_category(session, category_id)

    wallet: Wallet = await orm_get_wallet(session, wallet_id)
    transfer_wallet: Wallet = await orm_get_wallet(session, transfer_wallet_id)

    await orm_add_operation(
        session=session,
        user_id=user.id,
        wallet_id=wallet_id,
        amount=amount,
        comment=comment,
        operation_type=Operations.TRANSFER_TO.value,
        transfer_user_id=transfer_user.id,
        transfer_wallet_id=transfer_wallet_id,
        # category=category.title,
    )
    await orm_add_operation(
        session=session,
        user_id=transfer_user.id,
        wallet_id=transfer_wallet_id,
        amount=amount,
        comment=comment,
        operation_type=Operations.TRANSFER_FROM.value,
        transfer_user_id=user.id,
        transfer_wallet_id=wallet_id,
        category="",
    )
    await orm_edit_wallet_amount(session, wallet.id, wallet.amount - amount)
    await orm_edit_wallet_amount(session, transfer_wallet.id, transfer_wallet.amount + amount)

    await message.answer("Успешно!", reply_markup=get_callback_btns(
        btns={
            "Назад": f"wallets_page_{page}",
        }
    ))
    await state.clear()