from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from states.st_category_creation import st_Category_creation
from database.orm_query import orm_add_category
from services.profile_displayer import show_profile

router = Router()

@router.callback_query(F.data == "add_category")
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите название статьи")
    await state.set_state(st_Category_creation.title_state)

@router.message(st_Category_creation.title_state)
async def save_category(message: Message, state: FSMContext, session: AsyncSession):
    await orm_add_category(session, message.from_user.id, message.text)
    await state.clear()
    await show_profile(message.from_user.id, session)