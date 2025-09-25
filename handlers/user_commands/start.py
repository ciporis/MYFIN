from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.orm_query import orm_get_user_by_id
from states.st_registration import st_Registration
from services.profile_displayer import show_profile
from create_bot import bot
from keyboards.reply import remove

router = Router()

@router.message(CommandStart())
async def start_command_handler(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    user: User = await orm_get_user_by_id(session, message.from_user.id)

    if user is None:
        await state.set_state(st_Registration.fio_state)
        await bot.send_message(chat_id=message.chat.id, text="Здравствуйте, как к вам обращаться?", reply_markup=remove)
    else:
        await show_profile(message.from_user.id, session, state)