from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from services.constants.callbacks import WalletOperations
from states.st_wallet_creation import st_WalletCreation
from database.orm_query import orm_add_wallet, orm_add_operation
from services.profile_displayer import show_profile

router = Router()

@router.callback_query(F.data == WalletOperations.add_wallet)
async def handle_wallet_adding_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_wallet_creation(callback.message, state)

async def start_wallet_creation(message: Message, state: FSMContext):
    await message.answer("Название нового кошелька")
    await state.set_state(st_WalletCreation.title_state)

@router.message(st_WalletCreation.title_state)
async def save_wallet_title(message: Message, state: FSMContext):
    await state.update_data(wallet_title=message.text)
    await message.answer("Введите количество денег на кошельке, если он пуст, введите комманду /done")
    await state.set_state(st_WalletCreation.amount_state)

async def repeat_amount_input(message: Message, state: FSMContext):
    await message.answer("Введите число заново")
    await state.set_state(st_WalletCreation.amount_state)

@router.message(F.text, st_WalletCreation.amount_state)
async def save_wallet_amount(message: Message, state: FSMContext, session: AsyncSession):
    if message.text != "/done":
        if message.text.isdecimal():
            amount = float(message.text)
            await state.update_data(wallet_amount=amount)
            await create_wallet(message, state, session)

        else:
            await repeat_amount_input(message, state)
    else:
        await state.update_data(wallet_amount=0)
        await create_wallet(message, state, session)

async def create_wallet(message: Message, state: FSMContext, session: AsyncSession):
    state_data = await state.get_data()
    wallet_title = state_data["wallet_title"]
    wallet_amount = state_data["wallet_amount"]
    await orm_add_wallet(session, message.from_user.id, wallet_title, wallet_amount)
    await message.answer("Успешно")

    await show_profile(message.from_user.id, session)