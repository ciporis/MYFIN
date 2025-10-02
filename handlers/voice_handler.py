import os

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from create_bot import bot
from database.models import Wallet, Category, User, Operation
from database.orm_query import orm_get_wallet_by_title, orm_add_operation, orm_get_all_categories, \
    orm_get_user_with_wallets, orm_get_latest_wallet_operation, orm_delete_operation, orm_get_receivers, \
    orm_edit_wallet_amount
from services.constants import callbacks
from services.whisper_api import convert_voice_to_text
from services.openai import get_json_as_map
from services.profile_displayer import show_profile
from services.constants.operations import Operations
from services.openai import generate_text
from keyboards.inline import get_callback_btns

router = Router()

categories = [
    "Продукты питания",
    "Транспорт Жилье",
    "Кафе и рестораны",
    "Здоровье",
    "Одежда и обувь",
    "Развлечения",
    "Связь",
    "Личные расходы",
    "Накопления и инвестиции",
    "Прочее"
]

@router.message(F.voice | F.audio)
async def check_voice_message(message: types.Message, session: AsyncSession, state: FSMContext):
    user: User = await orm_get_user_with_wallets(session, message.from_user.id)
    current_wallet: Wallet = user.current_wallet

    if not user.is_subscribed:
        return

    wallets = [wallet.title for wallet in user.wallets]

    temp_mes = await message.answer("🔍 Начинаю анализ голосового сообщения...")
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    download_path = f"temp_voice_{message.from_user.id}.ogg"
    await bot.download_file(file.file_path, download_path)

    voice_text = await convert_voice_to_text(download_path)
    receivers = await orm_get_receivers(session, message.from_user.id)
    receiver_names = [rec.name for rec in receivers]
    print(receiver_names)
    prompt_template = """Проанализируй текст финансовой операции и верни данные СТРОГО в формате JSON. 

Требуемые поля:
- operation_type (обязательный): "Доход", "Расход" или "Перевод"
- wallet_name: название счета в именительном падеже или undefined (Доступные счета: {wallets})
- amount (обязательный): число (только цифры)
- comment (обязательный): описание операции
- receiver: получатель перевода (только для операций типа "Перевод"), иначе возвращай пустое значение. Пользователи, которым ранее исходил перевод({receivers})

Правила:
- Всегда возвращай валидный JSON
- Используй только undefined для отсутствующих значений, либо если receiver пустое значение
- Сумму извлекай как число
- wallet_name приводи к именительному падежу
- Если тип операции неясен, верни undefined для operation_type
- Для поля receiver сопоставляй с прошлыми получателями, если такого не найдешь, то возвращай нового получателя

Примеры ответов:
Текст: "Добавь расход 500 рублей на кофе"
Ответ: {{"operation_type": "Расход", "wallet_name": null, "amount": 500, "comment": "кофе", "receiver": ""}}

Текст: "Переведи 1000 с карты на наличные"
Ответ: {{"operation_type": "Перевод", "wallet_name": "карта", "amount": 1000, "comment": "перевод средств", "receiver": "наличные"}}

Текст: "Зарплата 50000 рублей на счет в банке"
Ответ: {{"operation_type": "Доход", "wallet_name": "счет в банке", "amount": 50000, "comment": "зарплата", "receiver": ""}}

Теперь проанализируй этот текст: "{voice_text}"
"""
    prompt = prompt_template.format(voice_text=voice_text, wallets=wallets, receivers=receiver_names)

    operation_as_json = await get_json_as_map(prompt=prompt)

    print("РАСПОЗНАЮ...")
    print(operation_as_json)

    undefined_fields_text = ("Извините, не смог обнаружить некоторые данные, отправьте голосовое сообщение снова, "
                             "не забудьте про название счёта, с которым проводите операцию")

    for key in operation_as_json.keys():
        if operation_as_json["wallet_name"] == "undefined":
            operation_as_json["wallet_name"] = current_wallet.title
        elif operation_as_json[key] == "undefined":
            await temp_mes.edit_text(text=undefined_fields_text)
            await show_profile(message.from_user.id, session, state)
            return

    wallet: Wallet = await orm_get_wallet_by_title(session, message.from_user.id, operation_as_json["wallet_name"])

    amount = float(operation_as_json["amount"])

    if amount <= 0 or wallet.amount - amount < 0:
        await temp_mes.edit_text(text="Некорректный ввод или не хватает средств!", reply_markup=get_callback_btns(
            btns={
                "Ок" : callbacks.ProfileCommands.show_profile,
            }
        ))

    os.remove(download_path)

    categories_text = ""

    user_categories = await orm_get_all_categories(session, message.from_user.id)

    for category in categories:
        categories_text += f"{category}\n"

    for category in user_categories:
        category: Category
        categories_text += f"{category.title}\n"

    category = ""

    temp_mes2 = None

    if operation_as_json["operation_type"] == Operations.OUTCOME.value:
        temp_mes2 = await temp_mes.edit_text(text="Определяю категорию расхода...")

        promt = (
            f"Определи по комментарию к расходу категорию, к которой он пренадлежит. В ответе напиши только название категори\n"
            f"Комментарий: {operation_as_json['comment']}\n"
            f"Категории: {categories_text}")

        category = await generate_text(promt)

    await orm_add_operation(
        session=session,
        user_id=message.from_user.id,
        wallet_id=wallet.id,
        amount=amount,
        comment=operation_as_json["comment"],
        operation_type=operation_as_json["operation_type"],
        receiver=operation_as_json["receiver"],
        category=category
    )

    new_amount = wallet.amount - amount

    await orm_edit_wallet_amount(session, wallet.id, new_amount)

    if not voice_text.strip():
        await message.answer("Не удалось распознать речь. Попробуйте записать сообщение ещё раз.")
        return

    text = (f"Проверьте правильность операции:\n"
            f"Счёт: {operation_as_json['wallet_name']}\n"
            f"Сумма: {operation_as_json['amount']}\n"
            f"Комментарий: {operation_as_json['comment']}\n"
            f"Тип операции: {operation_as_json['operation_type']}\n")

    if operation_as_json['operation_type'] == Operations.OUTCOME.value:
        text += f"Категория: {category}\n"
        message_to_edit = temp_mes2
    elif operation_as_json['operation_type'] == Operations.TRANSFER_TO.value:
        text += f"Получатель: {operation_as_json['receiver']}"
        message_to_edit = temp_mes
    else:
        message_to_edit = temp_mes

    lates_operation: Operation = await orm_get_latest_wallet_operation(session, wallet.id)

    await message_to_edit.edit_text(
        text=text,
        reply_markup=get_callback_btns(
            btns={
                "Отменить": f"cancel_operation_{lates_operation.id}",
                "Всё правильно": callbacks.ProfileCommands.show_profile
            }
        )
    )

@router.callback_query(F.data.startswith("cancel_operation_"))
async def delete_operation(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    await callback.answer()
    operation_id = int(callback.data.split("_")[-1])

    await orm_delete_operation(session, operation_id)
    await callback.message.delete()
    await show_profile(callback.from_user.id, session, state)
