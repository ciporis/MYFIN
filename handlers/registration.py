from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.st_registration import st_Registration
from keyboards.reply import phone_button, remove
from database.orm_query import orm_add_user
from services.profile_displayer import show_profile

router = Router()

@router.message(st_Registration.fio_state)
async def save_fio(message: Message, state: FSMContext):
    await state.update_data(fio = message.text)
    await message.answer("Отправьте ваш контакт",
                         reply_markup=await phone_button(text="Отправить контакт"))
    await state.set_state(st_Registration.phone_number_state)

@router.message(st_Registration.phone_number_state, F.contact)
async def save_contact(message: Message, state: FSMContext, session: AsyncSession):
    phone_number = message.contact.phone_number.replace('+', '')
    state_data = await state.get_data()
    fio = state_data[st_Registration.fio_key]
    await state.clear()
    await orm_add_user(session, message.from_user.id, fio, phone_number)
    await message.answer("Вы зарегистрированы", reply_markup=remove)
    await show_profile(message.from_user.id, session)