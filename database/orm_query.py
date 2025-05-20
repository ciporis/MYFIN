from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Operation

async def orm_add_user(session: AsyncSession, user_id: int, fio: str, phone_number: str):
    user: User = User(id=user_id, fio=fio, phone_number=phone_number, balance=float(0))
    session.add(user)
    await session.commit()

async def orm_get_user_by_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_update_user_balance(session: AsyncSession, user_id: int, amount: float):
    query = update(User).where(User.id == user_id).values(balance=amount)
    await session.execute(query)
    await session.commit()

async def orm_add_operation(session: AsyncSession, user_id: int,
                            amount: float, comment: str, operation_type: str,
                            transfer_user_id: int):
    operation = Operation(user_id=user_id,
                          amount=amount,
                          comment=comment,
                          operation_type=operation_type,
                          transfer_user_id=transfer_user_id,
                          )
    session.add(operation)
    await session.commit()

async def orm_get_user_by_phone_number(session: AsyncSession, phone_number: str):
    query = select(User).where(User.phone_number == phone_number)
    result = await session.execute(query)
    return result.scalar()

async def orm_get_all_operations(session: AsyncSession, user_id: int):
    query = select(Operation).where(Operation.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()