from sqlalchemy import Float, Integer, String, Text, DateTime, func, Date, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fio: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(Float)

class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(String)
    operation_type: Mapped[str] = mapped_column(String)
    transfer_user_id: Mapped[int] = mapped_column(BigInteger)