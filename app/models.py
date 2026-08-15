# from sqlalchemy import ForeignKey
# from datetime import datetime
# from app.database import Base
# from sqlalchemy.orm import Mapped, mapped_column
# from decimal import Decimal
#
# from app.enum import CurrencyEnum
#
#
# class User(Base):
#     __tablename__ = 'user'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     login : Mapped[int] = mapped_column(unique = True)
#
#
#
#
# class Wallet(Base):
#     __tablename__ = 'wallet'
#
#     id : Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]
#     balance: Mapped[Decimal]
#     user_id : Mapped[int] = mapped_column(ForeignKey('user.id'), nullable = False)
#
#     currency : Mapped[CurrencyEnum]
#
#
# class Operation(Base):
#     __tablename__ = 'operation'
#     id : Mapped[int] = mapped_column(primary_key=True)
#     wallet_id : Mapped[int] = mapped_column(ForeignKey('wallet.id'), nullable = False)
#     type:Mapped[Decimal]
#     currency: Mapped[CurrencyEnum] = mapped_column(default = None)
#     category: Mapped[str|None] = mapped_column(default=None)
#     created_at: Mapped[datetime] = mapped_column(default=lambda : datetime.now())



from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import ForeignKey, String, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enum import CurrencyEnum, OperationType  # Если есть Enum типов операций


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    wallets: Mapped[list["Wallet"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Wallet(Base):
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[Decimal] = mapped_column(default=Decimal("0.00"), nullable=False)
    currency: Mapped[CurrencyEnum] = mapped_column(SQLEnum(CurrencyEnum), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped["User"] = relationship(back_populates="wallets")
    operations: Mapped[list["Operation"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")


class Operation(Base):
    __tablename__ = 'operation'

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey('wallet.id'), nullable=False)

    type: Mapped[OperationType] = mapped_column(SQLEnum(OperationType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(nullable=False)

    currency: Mapped[CurrencyEnum | None] = mapped_column(SQLEnum(CurrencyEnum), nullable=True, default=None)
    category: Mapped[str | None] = mapped_column(String(100), default=None, nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )

    # Связи
    wallet: Mapped["Wallet"] = relationship(back_populates="operations")