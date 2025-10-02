import datetime

from aiogram import F, types, Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Promocode
from database.orm_query import orm_get_all_promocodes, orm_edit_user_is_subscribed, orm_edit_user_end_date, \
    orm_edit_user_used_promocode
from handlers.filters.chat_types import ChatTypeFilter
from create_bot import bot
from keyboards.inline import get_callback_btns
from services.constants import callbacks

router = Router()

router.message.filter(ChatTypeFilter(["private"]))

class st_Promocode_Using(StatesGroup):
    check_title_state = State()

@router.message(Command("promocode"))
async def use_promocode(message: types.Message, state: FSMContext):
    await message.answer("Промокод:")
    await state.set_state(st_Promocode_Using.check_title_state)

@router.message(st_Promocode_Using.check_title_state)
async def check_promocode(message: Message, state: FSMContext, session: AsyncSession, apscheduler: AsyncIOScheduler):
    promocodes = await orm_get_all_promocodes(session)

    for promocode in promocodes:
        promocode: Promocode

        if promocode.title == message.text:
            end_date = datetime.datetime.now() + datetime.timedelta(days=30)

            await orm_edit_user_is_subscribed(session, message.from_user.id, True)
            await orm_edit_user_end_date(session, message.from_user.id, end_date)
            await orm_edit_user_used_promocode(session, message.from_user.id, True)

            apscheduler.add_job(
                func=send_notification,
                trigger="date",
                run_date=end_date - datetime.timedelta(days=1),
                kwargs={"chat_id": message.chat.id},
            )

            apscheduler.add_job(
                func=delete_sub_end_date,
                trigger="date",
                run_date=end_date,
                kwargs={"user_id": message.from_user.id, "chat_id": message.chat.id, "session": session},
            )

            await message.answer(text="Промокод успешно применён!", reply_markup=get_callback_btns(
                btns={
                    "Назад" : callbacks.ProfileCommands.show_profile
                }
            ))

            break

async def send_notification(chat_id: int):
    await bot.send_message(
        chat_id=chat_id,
        text=f"!!!До окончания подписки остался 1 день!!!"
    )

async def delete_sub_end_date(user_id: int, chat_id: int, session: AsyncSession):
    await orm_edit_user_end_date(session, user_id, None)
    await orm_edit_user_is_subscribed(session, user_id, False)
    await bot.send_message(chat_id=chat_id, text="!!!Срок подписки истёк!!!")