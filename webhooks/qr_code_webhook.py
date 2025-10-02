from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiohttp import web
from fnsapi.api import FNSApi

from database.engine import session_maker
from database.models import Category
from database.orm_query import orm_get_all_categories
from services.openai import get_json_as_map


async def qr_code_webhook(request):
    # fns_api = FNSApi()

    # session_token = fns_api.get_session_token()

    try:
        query_params = request.query

        user_id = int(query_params.get("user_id"))
        s = int(float(query_params.get("s")) * 100)
        parsed_key = datetime.strptime(query_params.get("t"), "%Y%m%dT%H%M")
        t = datetime.strftime(parsed_key, "%Y%m%dT%H%M")
        fn = query_params.get("fn")
        n = query_params.get("n")
        i = query_params.get("i")
        fp = query_params.get("fp")
        # result = fns_api.get_ticket(
        #     session_token=session_token,
        #     user_id=user_id,
        #     sum=qr_data['s'],  # сумма чека в формате РРРКК, 12 рублей 23 копейки передавайте как 1223
        #     timestamp=qr_data['t'],  # дата и время в формате %Y-%m-%dT%H:%M:%S
        #     fiscal_number=qr_data['fn'],  # код ККТ
        #     operation_type=qr_data['n'],  # тип операции
        #     fiscal_document_id=qr_data['i'],  # номер фискального документа
        #     fiscal_sign=qr_data['fp']  # фискальный признак
        # )

        # status = result['status']  # success, если апи фНС отработало запрос, еrror, если нет.
        # code = result['code']  # код ошибки от апи ФНС.
        # message = result['message']  # сообщение от ФНС в случае ошибки или JSON-строка с информацией о чеке.

        default_categories = [
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
        async with session_maker() as session:
            user_categories = await orm_get_all_categories(session, user_id)
            print(user_categories)

        user_categories_titles = [category.title for category in user_categories]

        categories = default_categories + user_categories_titles

        promt = f"""
Роль: Ты — опытный финансовый аналитик, который специализируется на категоризации и анализе потребительских расходов. 
Твоя задача — точно и без лишних слов относить товары к заданным категориям.

Входные данные:
#JSON WITH RECEIPT DATA

Список существующих категорий расходов:
{categories}

Задача: Преобразовать входные данные в итоговый JSON, сгруппировав все товары по категориям и просуммировав их стоимость.

Выходные данные (Требуемый формат):
jsonс такими полями:
"category1": "total_amount1",
"category2": "total_amount2",
...
Правила и инструкции по выполнению:

Анализ товаров: Тщательно проанализируй название каждого товара из входного JSON. На основе его названия определи, к 
какой категории из предоставленного списка он относится.

Группировка и суммирование: Собери все товары, относящиеся к одной категории, и просуммируй их стоимость.

Формат вывода:
Выводи ТОЛЬКО валидный JSON-объект, без каких-либо пояснений, комментариев или Markdown-разметки (никаких ```json в начале).
Ключами в объекте должны быть строки с названиями категорий.
Значениями должны быть строки, содержащие итоговую сумму для этой категории.
Категории, для которых в чеке не нашлось товаров, включать в ответ НЕ НУЖНО.
        """

        # determined_categories_with_totals: dict = await get_json_as_map(promt)

        #ADD OPERATION IN BASE

        return web.Response(status=200)
    except:
        return web.Response(status=403)

def parse_query_qr_string(query_str):
    result = {}
    pairs = query_str.split('&')

    for pair in pairs:
        key, value = pair.split('=', 1)

        if key == 't':
            parsed_key = datetime.strptime(value, "%Y%m%dT%H%M")
            value = parsed_key.strftime("%Y-%m-%dT%H:%M:%S")
        elif key == 's':
            value = int(float(value) * 100)

        result[key] = value

    return result