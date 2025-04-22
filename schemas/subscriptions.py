from sqlalchemy import String, Float, DateTime, ForeignKey, UUID, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from uuid import uuid4
from .users import User
from enum import Enum


class ValidSubscriptionStatus(str, Enum):
    PROCESSING = "Processing"
    ACTIVE = "Active"
    CANCELED = "Cancelled"
    ENDED = "Ended"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid4,
        comment="Primary key for Subscription"
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        comment="Foreign key to the Users Table"
    )

    source_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Stripe Source ID (if any)"
    )

    currency: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Currency Type of the Subscription"
    )

    amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Amount Charged for the Subscription"
    )

    started_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Subscription Start Time"
    )

    ended_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Subscription End Time"
    )

    canceled_at: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Time at which Subscription was Canceled"
    )

    status: Mapped[ValidSubscriptionStatus] = mapped_column(
        SQLEnum(ValidSubscriptionStatus, name="valid_subscription_status"),
        default=ValidSubscriptionStatus.PROCESSING,
        nullable=False,
        comment="Current Status of the Subscription"
    )

    ###############
    # Relationship
    ###############

    user: Mapped["User"] = relationship()
