from sqlalchemy import String, Float, DateTime, ForeignKey, UUID, Enum as SQLAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from uuid import uuid4
from .users import User
from enum import Enum
from .transactions import Transaction


class ValidAccountStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    CLOSED = "Closed"
    

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Primary key for Accounts"
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to the Users Table"
    )
    
    currency: Mapped[str] = mapped_column(
        String(5),
        default="USD",
        nullable=False,
        comment="Currency Type of the Balance"
    )

    balance: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Balance of the Account"
    )

    last_updated: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Time the Account Balance was Last Updated"
    )

    status: Mapped[ValidAccountStatus] = mapped_column(
        SQLAEnum(ValidAccountStatus, name="valid_account_status"),
        default=ValidAccountStatus.ACTIVE,
        nullable=False,
        comment="Current Status of the Account"
    )

    ################
    # Relationships
    ################
    
    user: Mapped["User"] = relationship()
    
    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.sender_account_id]",
        cascade="all, delete-orphan"
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="[Transaction.receiver_account_id]",
        cascade="all, delete-orphan"
    )
