import datetime
import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup

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

class st_AddCategory(StatesGroup):
    add_category = State()

questions = ["Как исправить операцию, если я ошибся в сумме или комментарии?",
             "Переводы происходят между пользователями бота?",
             "Как добавить чек через QR-код?",
             "Что даёт Premium-подписка?"]
answers = ["К сожалению, в текущей версии бота "
           "редактирование операций недоступно. "
           "Если вы ошиблись, просто создайте "
           "новую операцию с правильными данными. "
           "Мы уже работаем над функцией редактирования "
           "и удаления записей — она появится в "
           "одном из следующих обновлений.",
           "Нет. Перевод в нашем боте — это лишь запись о переводе денег "
           "другому лицу (например, другу или организации). Фактического "
           "перевода средств внутри системы не происходит. Эта функция "
           "помогает вам учитывать, кому и сколько вы должны или кто должен "
           "вам.",
           "Нажмите кнопку «Добавить чек» в главном меню — откроется мини-приложение для"
           " сканирования QR-кода. Данные с чека автоматически добавятся в базу данных.",
           "С нашей подпиской вам станет доступны:\n\n"
           "1) Обработка голосовых сообщений\n"
           "2) Сканер чеков\n"
           "3) Удобный вывод статистики\n"
           "4) Возможность иметь больше одного счёта\n"
           "5) Возможность добавлять свои категории расходов"
           ]

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    current_wallet: Wallet = user.current_wallet

    print(current_wallet.is_hidden)

    if current_wallet.is_hidden is True:
        buttons = {
            "FAQ": callbacks.FAQ,
            "Тех поддержка": "https://t.me/+8OUgQH2HdJkzNTQ6",
            "Категории расходов": callbacks.outcome_categories,
            "Отобразить счёт": callbacks.change_wallet_state,
            "Премиум": callbacks.premium,
            "Назад": callbacks.ProfileCommands.show_profile
        }
    else:
        buttons = {
            "FAQ" : callbacks.FAQ,
            "Тех поддержка" : "https://t.me/+8OUgQH2HdJkzNTQ6",
            "Категории расходов" : callbacks.outcome_categories,
            "Скрыть счёт" : callbacks.change_wallet_state,
            "Премиум" : callbacks.premium,
            "Назад" : callbacks.ProfileCommands.show_profile
        }

    sizes = (2, 2, 1, 1, )

    await callback.message.edit_text("Настройки", reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))

# FAQ
@router.callback_query(F.data == callbacks.FAQ)
async def show_faq(callback: CallbackQuery, state: FSMContext):
    buttons = {}

    for question in questions:
        buttons[question] = f"show_answer_{questions.index(question)}"

    buttons["Назад"] = callbacks.settings

    await callback.message.edit_text(text="FAQ", reply_markup=get_callback_btns(
        btns=buttons,
    ))

@router.callback_query(F.data.startswith("show_answer_"))
async def show_answer(callback: CallbackQuery):
    answer = answers[int(callback.data.split('_')[-1])]

    await callback.message.edit_text(text=answer, reply_markup=get_callback_btns(
        btns={
            "Назад" : callbacks.FAQ,
        },
    ))

# Categories
@router.callback_query(F.data == callbacks.outcome_categories)
async def show_categories(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    user: User = await orm_get_user_by_id(session, callback.from_user.id)

    all_categories = "Категории:\n\n"

    default_categories = [
        "Продукты питания",
        "Транспорт",
        "Жилье",
        "Кафе и рестораны",
        "Здоровье",
        "Одежда и обувь",
        "Развлечения",
        "Связь",
        "Личные расходы",
        "Накопления и инвестиции",
        "Прочее"
    ]
    user_categories = await orm_get_all_categories(session, callback.from_user.id)

    for category in default_categories:
        all_categories += f"{category}\n"

    buttons = {}

    if user.is_subscribed:
        for category in user_categories:
            category: Category
            buttons[category.title] = f"edit_category_{category.id}\n"

        buttons["Добавить"] = f"add_category"

    buttons["Назад"] = callbacks.settings

    await callback.message.edit_text(text=all_categories, reply_markup=get_callback_btns(
        btns=buttons,
    ))

@router.callback_query(F.data == "add_category")
async def add_category(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.message.edit_text("Введите название")
    await state.set_state(st_AddCategory.add_category)

@router.message(st_AddCategory.add_category)
async def save_category_title(message: Message, session: AsyncSession, state: FSMContext):
    await orm_add_category(session, message.from_user.id, message.text)
    user: User = await orm_get_user_by_id(session, message.from_user.id)

    all_categories = "Категории:\n\n"

    default_categories = [
        "Продукты питания",
        "Транспорт",
        "Жилье",
        "Кафе и рестораны",
        "Здоровье",
        "Одежда и обувь",
        "Развлечения",
        "Связь",
        "Личные расходы",
        "Накопления и инвестиции",
        "Прочее"
    ]
    user_categories = await orm_get_all_categories(session, message.from_user.id)

    for category in default_categories:
        all_categories += f"{category}\n"

    buttons = {}

    if user.is_subscribed:
        for category in user_categories:
            category: Category
            buttons[category.title] = f"edit_category_{category.id}\n"

        buttons["Добавить"] = f"add_category"

    buttons["Назад"] = callbacks.settings

    await message.answer(text=all_categories, reply_markup=get_callback_btns(
        btns=buttons,
    ))

@router.callback_query(F.data.startswith("edit_category_"))
async def edit_category(callback: CallbackQuery, session: AsyncSession):
    category_id: int = int(callback.data.split('_')[-1])

    category: Category = await orm_get_category(session, category_id)

    buttons = {
        "Изменить" : f"change_category_title_{category_id}",
        "Удалить" : f"delete_category_{category_id}",
        "Назад" : callbacks.outcome_categories,
    }

    await callback.message.edit_text(text=f"{category.title}", reply_markup=get_callback_btns(
        btns=buttons,
        sizes=(2, 1, ),
    ))

@router.callback_query(F.data.startswith("change_category_title_"))
async def edit_category_title(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    category_id: int = int(callback.data.split('_')[-1])
    await state.update_data(category_id=category_id)

    await callback.message.edit_text(text="Новое навзание категории:")
    await state.set_state(st_Category.edit_title_state)

@router.message(st_Category.edit_title_state)
async def save_edited_category_title(message: Message, session: AsyncSession, state: FSMContext):
    state_data = await state.get_data()

    category_id: int = int(state_data["category_id"])

    await orm_edit_category_title(session, category_id, message.text)

    user: User = await orm_get_user_by_id(session, message.from_user.id)

    all_categories = "Категории:\n\n"

    default_categories = [
        "Продукты питания",
        "Транспорт",
        "Жилье",
        "Кафе и рестораны",
        "Здоровье",
        "Одежда и обувь",
        "Развлечения",
        "Связь",
        "Личные расходы",
        "Накопления и инвестиции",
        "Прочее"
    ]
    user_categories = await orm_get_all_categories(session, message.from_user.id)

    for category in default_categories:
        all_categories += f"{category}\n"

    buttons = {}

    if user.is_subscribed:
        for category in user_categories:
            category: Category
            buttons[category.title] = f"edit_category_{category.id}\n"

        buttons["Добавить"] = f"add_category"

    buttons["Назад"] = callbacks.settings

    await message.answer(text=all_categories, reply_markup=get_callback_btns(
        btns=buttons,
    ))

    await state.clear()

@router.callback_query(F.data.startswith("delete_category_"))
async def delete_category(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    category_id: int = int(callback.data.split('_')[-1])

    await orm_delete_category(session, category_id)
    await callback.message.delete()

    user: User = await orm_get_user_by_id(session, callback.from_user.id)

    all_categories = "Категории:\n\n"

    default_categories = [
        "Продукты питания",
        "Транспорт",
        "Жилье",
        "Кафе и рестораны",
        "Здоровье",
        "Одежда и обувь",
        "Развлечения",
        "Связь",
        "Личные расходы",
        "Накопления и инвестиции",
        "Прочее"
    ]
    user_categories = await orm_get_all_categories(session, callback.from_user.id)

    for category in default_categories:
        all_categories += f"{category}\n"

    buttons = {}

    if user.is_subscribed:
        for category in user_categories:
            category: Category
            buttons[category.title] = f"edit_category_{category.id}\n"

        buttons["Добавить"] = f"add_category"

    buttons["Назад"] = callbacks.settings

    await bot.send_message(chat_id=user.id, text=all_categories, reply_markup=get_callback_btns(
        btns=buttons,
    ))

    await state.clear()

# Hide wallet
@router.callback_query(F.data == callbacks.change_wallet_state)
async def hide_wallet(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    current_wallet: Wallet = user.current_wallet

    wallet_is_hidden = not current_wallet.is_hidden

    print(current_wallet.title)
    print(f"Current wallet is hidden {wallet_is_hidden}")

    await orm_edit_wallet_is_hidden(session, current_wallet.id, wallet_is_hidden)

    user: User = await orm_get_user_by_id(session, callback.from_user.id)
    current_wallet: Wallet = user.current_wallet

    if current_wallet.is_hidden is True:
        buttons = {
            "FAQ": callbacks.FAQ,
            "Тех поддержка": "https://t.me/+8OUgQH2HdJkzNTQ6",
            "Категории расходов": callbacks.outcome_categories,
            "Отобразить счёт": callbacks.change_wallet_state,
            "Премиум": callbacks.premium,
            "Назад": callbacks.ProfileCommands.show_profile
        }
    else:
        buttons = {
            "FAQ": callbacks.FAQ,
            "Тех поддержка": "https://t.me/+8OUgQH2HdJkzNTQ6",
            "Категории расходов": callbacks.outcome_categories,
            "Скрыть счёт": callbacks.change_wallet_state,
            "Премиум": callbacks.premium,
            "Назад": callbacks.ProfileCommands.show_profile
        }

    sizes = (2, 2, 1, 1,)

    await callback.message.edit_text("Настройки", reply_markup=get_callback_btns(
        btns=buttons,
        sizes=sizes
    ))

# Premium
@router.callback_query(F.data == callbacks.premium)
async def show_premium(callback: CallbackQuery, state: FSMContext):
    text=("С нашей подпиской вам станет доступны:\n\n"
          "1) Обработка голосовых сообщений\n"
          "2) Сканер чеков\n"
          "3) Удобный вывод статистики\n"
          "4) Возможность иметь больше одного счёта\n"
          "5) Возможность добавлять свои категории расходов")

    await callback.message.edit_text(text=text, reply_markup=get_callback_btns(
        btns={
            "Купить" : "buy_subscription",
            "Назад" : callbacks.settings,
        }
    ))

@router.callback_query(F.data == "buy_subscription")
async def send_money(call: CallbackQuery):
    load_dotenv(find_dotenv())

    payment_token = os.getenv("UKASSA_TOKEN")

    description = (
        f"Оплатите ваш заказ на сумму {400} рубелй"
    )
    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оплата подписки в приложении на [{400}₽]',
        description=description,
        payload=f'donate_{400}',
        currency='RUB',
        prices=[LabeledPrice(label="Заказ", amount=400*100)],
        provider_token=payment_token
    )

    await call.answer()

@router.pre_checkout_query()
async def user_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def user_successful_payment(message: Message, session: AsyncSession, apscheduler: AsyncIOScheduler):
    end_date: datetime.date = datetime.date.today() + datetime.timedelta(days=30)

    apscheduler.add_job(
        func=send_notification,
        trigger="date",
        run_date=end_date - datetime.timedelta(days=1),
        kwargs={ "chat_id" : message.chat.id},
    )

    apscheduler.add_job(
        func=delete_sub_end_date,
        trigger="date",
        run_date=end_date,
        kwargs={"user_id": message.from_user.id, "chat_id": message.chat.id, "session" : session},
    )

    await orm_edit_user_end_date(session, message.from_user.id, sub_end_date=end_date)
    await orm_edit_user_is_subscribed(session, message.from_user.id, True)
    await message.answer(f"Ваш заказ на сумму {400}₽ оформлен")

async def send_notification(chat_id: int):
    await bot.send_message(
        chat_id=chat_id,
        text=f"!!!До окончания подписки осталось {1} дней!!!"
    )

async def delete_sub_end_date(user_id: int, chat_id: int, session: AsyncSession):
    await orm_edit_user_end_date(session, user_id, None)
    await orm_edit_user_is_subscribed(session, user_id, False)
    await bot.send_message(chat_id=chat_id, text="!!!Срок подписки истёк!!!")