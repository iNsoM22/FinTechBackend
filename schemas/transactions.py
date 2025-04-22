from sqlalchemy import Float, DateTime, ForeignKey, UUID, String, Enum as SQLAEnum, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
from uuid import uuid4
from enum import Enum


class ValidTransactionStatus(str, Enum):
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    REJECTED = "Rejected"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Unique Primary key for Transactions"
    )
    
    sender_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to the sender's Account"
    )
    
    receiver_account_id: Mapped[UUID] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to the receiver's Account"
    )
    
    sender_username: Mapped[str] = mapped_column(
        String(256), 
        nullable=False,
        comment="Username of the Sender"
    )
    
    receiver_username: Mapped[str] = mapped_column(
        String(256), 
        nullable=False,
        comment="Username of the Receiver"
    )
    
    
    transfer_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        comment="Transferred amount"
    )

    made_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Time when the Transaction was made"
    )

    status: Mapped[ValidTransactionStatus] = mapped_column(
        SQLAEnum(ValidTransactionStatus, name="valid_transaction_status"),
        default=ValidTransactionStatus.PROCESSING,
        nullable=False,
        comment="Status of the Transaction"
    )
