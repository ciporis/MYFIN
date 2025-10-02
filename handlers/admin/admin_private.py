from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup

from create_bot import bot
from database.models import User, Promocode
from database.orm_query import orm_get_all_users, orm_get_all_promocodes, orm_delete_promocode, orm_add_category, \
    orm_add_promocode
from handlers.filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.inline import get_callback_btns
from keyboards.reply import get_keyboard
from services.constants import callbacks

router = Router()
router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

class st_Promocode(StatesGroup):
    title_state = State()
    percent_state = State()

class st_Newsletter(StatesGroup):
    message_state = State()

@router.message(Command("admin"))
async def show_info_for_admin(message: Message, session: AsyncSession):
    users = await orm_get_all_users(session)

    used_promocode_amount = 0
    is_subscribed_amount = 0
    amount = 0

    for user in users:
        user: User

        amount += 1

        if user.is_subscribed:
            is_subscribed_amount += 1
        elif user.used_promocode:
            used_promocode_amount += 1

    text = (f"Кол-во пользователей: {amount}\nPremium пользователи: {is_subscribed_amount}\n\n"
            f"Активации промокодов: {used_promocode_amount}")

    await message.answer(text)

@router.message(Command("promocodes"))
async def show_promocodes(message: Message, session: AsyncSession):
    promocodes = await orm_get_all_promocodes(session)

    text = "Нажмите на промокод, чтобы его УДАЛИТЬ"

    buttons={}

    for promocode in promocodes:
        promocode: Promocode
        buttons[f"{promocode.title} - {promocode.percent}%"] = f"delete_promocode_{promocode.id}"

    buttons["Добавить"] = "add_promocode"

    await message.answer(text=text, reply_markup=get_callback_btns(
        btns=buttons
    ))


@router.callback_query(F.data.startswith("delete_promocode_"))
async def delete_promocode(callback: CallbackQuery, session: AsyncSession):
    promo_id = int(callback.data.split('_')[-1])
    await orm_delete_promocode(session, promo_id)
    await callback.message.edit_text(text="Успешно!")

@router.callback_query(F.data == "add_promocode")
async def add_promocode(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.edit_text(text="Название промокода:")
    await state.set_state(st_Promocode.title_state)


@router.message(st_Promocode.title_state)
async def save_promocode_title(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(promocode_title=message.text)
    await message.answer(text="Процент промокода:")
    await state.set_state(st_Promocode.percent_state)

@router.message(st_Promocode.percent_state)
async def save_promocode_percent(message: Message, session: AsyncSession, state: FSMContext):
    state_date = await state.get_data()
    title = state_date["promocode_title"]
    await orm_add_promocode(session, title, float(message.text))
    await message.answer(text="Успешно!")

# SENDING
@router.message(Command("newsletter"))
async def ask_for_message(message: Message, session: AsyncSession, state: FSMContext):
    await message.answer(text="Сообщение, которое нужно разослать всем:")
    await state.set_state(st_Newsletter.message_state)

@router.message(st_Newsletter.message_state)
async def send_message(message: Message, session: AsyncSession, state: FSMContext):
    users = await orm_get_all_users(session)

    for user in users:
        user: User
        await bot.send_message(user.id, message.text)

    await message.answer(text="Успешно разослано!", reply_markup=get_callback_btns(
        btns={
            "Назад" : callbacks.ProfileCommands.show_profile
        })
    )