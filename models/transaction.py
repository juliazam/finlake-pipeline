# pylint: disable=not-callable
from datetime import datetime
import enum
from decimal import Decimal
from sqlalchemy import Enum as SAEnum, String, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DENIED = "denied"

class Transaction(Base):
    __tablename__ = 'transactions'

    record_id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    account_id: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True, server_default='SGD')
    status: Mapped[TransactionStatus] = mapped_column(
        SAEnum(TransactionStatus, name='transaction_status'),
        nullable=False
    )
    merchant: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()
    )
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
