from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import datetime

from handlers.wallet_maker import start_wallet_creation
from states.st_registration import st_Registration
from keyboards.reply import phone_button, remove
from database.orm_query import orm_add_user
from create_bot import bot

router = Router()

@router.message(st_Registration.fio_state)
async def save_fio(message: Message, state: FSMContext):
    await state.update_data(fio = message.text)
    await message.answer("Отправьте ваш номер телефона", reply_markup=await phone_button(text="Отправить контакт"))
    await state.set_state(st_Registration.phone_number_state)

@router.message(st_Registration.phone_number_state, F.contact)
async def save_contact(message: Message, state: FSMContext, session: AsyncSession, apscheduler: AsyncIOScheduler):
    phone_number = message.contact.phone_number.replace('+', '')
    state_data = await state.get_data()
    fio = state_data[st_Registration.fio_key]
    await state.clear()
    await orm_add_user(session, message.from_user.id, fio, phone_number)
    await message.answer("Вы зарегистрированы", reply_markup=remove)

    date = datetime.datetime.now()
    date_week1 = date + datetime.timedelta(minutes=2)
    date_week2 = date + datetime.timedelta(hours=2)

    user_id = message.from_user.id
    job_id = f'{user_id}_{date}_00:00'

    apscheduler.add_job(send_ad_offer, id=f'{job_id}_g', trigger='date', run_date=date_week1, kwargs={
        'chat_id': user_id})
    apscheduler.add_job(send_ad_offer, id=f'{job_id}_q', trigger='date', run_date=date_week2, kwargs={
        'chat_id': user_id})

    await message.answer("Давайте добавим счёт!")
    await start_wallet_creation(message, state)

@router.message(st_Registration.phone_number_state)
async def handle_text_in_contact_state(message: Message, state: FSMContext):
    await message.answer("Отправьте ваш номер (кнопка внизу)")

async def send_ad_offer(chat_id: int):
    await bot.send_message(chat_id, """Хотите больше контроля и точности?
 Сейчас вы используете базовую версию Аналитика Бота. Чтобы раскрыть весь потенциал финансового анализа, выберите подходящий тариф:
🔹 Эконом — для старта: базовая аналитика, учёт расходов и прибыли
🔹 Комфорт — расширенные отчёты, категории, рекомендации от нейросети
🔹 Бизнес — максимальная детализация, отчёты по отделам и проектам, прогнозы и приоритетная поддержка
Каждый тариф — это шаг к тому, чтобы лучше понимать свой бизнес и принимать точные решения.
📊 Выберите тариф и управляйте финансами уверенно.
Telegram: @ACR3LIS
""")


