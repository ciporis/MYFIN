import datetime
import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from yookassa import Payment, Configuration

import services.profile_displayer
from create_bot import bot
from database.orm_query import orm_get_user_by_id, orm_get_all_categories, orm_get_category, orm_add_category, \
    orm_edit_category_title, orm_delete_category, orm_edit_wallet_is_hidden, orm_edit_user_end_date, \
    orm_edit_user_is_subscribed
from keyboards.inline import get_callback_btns
from services.constants import callbacks
from database.models import User, Category, Wallet
from states.st_category import st_Category
from services.constants.callbacks import ProfileCommands

router = Router()

Configuration.account_id = os.getenv('UKASSA_SHOP_ID')
Configuration.secret_key = os.getenv('UKASSA_SECRET_KEY')

# Premium
@router.callback_query(F.data == "buy_subscription")
async def show_premium(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.from_user.id

    await orm_edit_user_is_subscribed(session, user_id, True)
    await callback.answer("Ваша подписка активирована!", show_alert=True)

    # try:
    #     payment = await create_payment(
    #         amount=149.00,
    #         description="Подписка на MYFIN",
    #         user_id=user_id
    #     )
    #
    #     payment_url = payment.confirmation.confirmation_url
    #
    #     await callback.message.edit_text(
    #         "Для завершения оплаты нажмите на кнопку ниже:\n\n"
    #         f"ID платежа: `{payment.id}`",
    #         reply_markup=get_callback_btns(
    #             btns={
    #                 "Оплатить" : payment_url
    #             }
    #         ),
    #     )
    #
    # except Exception as e:
    #     await callback.message.edit_text(
    #         f"Произошла ошибка при создании платежа: {str(e)}"
    #     )

async def create_payment(amount: float, description: str, user_id: int):
    return_url = "https://t.me/FinAccounting_test_bot"

    payment = Payment.create({
        "amount": {
            "value": f"{amount:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "description": f"{description}",
        "metadata": {
            "user_id": user_id,
        },
        "save_payment_method": True
    })

    return payment