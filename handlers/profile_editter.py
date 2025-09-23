from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline import get_callback_btns
from keyboards.reply import phone_button
from services.constants.callbacks import ProfileCommands, WalletOperations
from services.profile_displayer import show_profile
from states.st_user_commands import st_User_Commands
from database.orm_query import orm_edit_user_fio, orm_edit_user_phone_number

router = Router()

@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery):
    await callback.message.edit_text("Настройки", reply_markup=get_callback_btns(
        btns={
            "Добавить кошелек" : WalletOperations.add_wallet,
            "Добавить статью расходов" : "add_category",
            "Изменить ФИО": "edit_fio",
            "Изменить номер": "edit_contact",
            "Назад" : ProfileCommands.show_profile
        }
    ))

@router.callback_query(F.data == "edit_fio")
async def edit_fio(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Новое ФИО")
    await state.set_state(st_User_Commands.st_EditProfile.fio_state)

@router.message(st_User_Commands.st_EditProfile.fio_state)
async def save_edited_fio(message: Message, state: FSMContext, session: AsyncSession):
    await orm_edit_user_fio(session, message.from_user.id, message.text)
    await show_profile(message.from_user.id, session)
    await state.clear()

@router.callback_query(F.data == "edit_contact", F.contact)
async def edit_phone_number(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Новый контакт", reply_markup=await phone_button("Отправить"))
    await state.set_state(st_User_Commands.st_EditProfile.phone_number_state)

@router.message(st_User_Commands.st_EditProfile.phone_number_state)
async def save_edited_fio(message: Message, state: FSMContext, session: AsyncSession):
    await orm_edit_user_phone_number(session, message.from_user.id, message.contact.phone_number.replace('+', ''))
    await show_profile(message.from_user.id, session)
    await state.clear()