import json

from datetime import datetime

from aiohttp import web

from database.engine import session_maker
from database.models import Category, User
from database.orm_query import orm_get_all_categories, orm_get_wallet_operations_from_to_as_json, orm_get_user_by_id
from services.openai import get_json_as_map


async def premium_operations_history_webhook(request):
    try:
        query_params = request.query
        print("BEBRA")
        user_id = int(query_params.get("user_id"))
        start_date = datetime.strptime(query_params.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(query_params.get("end_date"), "%Y-%m-%d")

        async with session_maker() as session:
            user: User = await orm_get_user_by_id(session, user_id)
            wallet_operations_from_to_as_json = await orm_get_wallet_operations_from_to_as_json(session,
                                                                                                user.current_wallet_id,
                                                                                                start_date, end_date)
        json_string = json.dumps(wallet_operations_from_to_as_json, ensure_ascii=False, default=str)

        return web.Response(content_type='application/json', text=json_string, status=200)
    except:
        return web.Response(status=403)