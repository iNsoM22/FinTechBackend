from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.accounts import ValidAccountStatus
from schemas.transactions import ValidTransactionStatus
from schemas.subscriptions import ValidSubscriptionStatus


# Base Schema for Account
class AccountBase(BaseModel):
    user_id: UUID = Field(
        ...,
        description="User ID who owns this Account"
    )
    currency: str = Field(
        default="USD",
        description="Currency type for the Account"
    )
    balance: float = Field(
        default=0.0,
        description="Current Balance in the Account"
    )
    status: ValidAccountStatus = Field(
        default=ValidAccountStatus.ACTIVE,
        description="Account's current status"
    )

    model_config = ConfigDict(from_attributes=True)


# Request Model for Creating an Account
class AccountCreateRequest(AccountBase):
    pass


# Request Model for Updating an Account
class AccountUpdateRequest(BaseModel):
    currency: Optional[str] = Field(
        default=None, description="Updated Currency"
    )
    status: Optional[ValidAccountStatus] = Field(
        default=None, description="Updated Account Status"
    )

    model_config = ConfigDict(from_attributes=True)


# Response Model for Account Read
class AccountResponse(AccountBase):
    id: UUID = Field(
        ..., description="Unique Account ID"
    )
    last_updated: datetime = Field(
        ..., description="Timestamp of Last Balance Update"
    )

class AccountBalanceResponse(BaseModel):
    currency: str = Field(
        default="USD",
        description="Currency type for the Account"
    )
    balance: float = Field(
        default=0.0,
        description="Current Balance in the Account"
    )
    last_updated: datetime = Field(
        ...,
        description="Timestamp of Last Balance Update"
    )

    model_config = ConfigDict(from_attributes=True)


    

# # Response Model with Transactions
# class AccountResponseWithTransactions(AccountResponse):
#     sent_transactions: List["TransactionResponseLite"] = Field(
#         default_factory=list, description="List of Sent Transactions"
#     )
#     received_transactions: List["TransactionResponseLite"] = Field(
#         default_factory=list, description="List of Received Transactions"
#     )


# Base Schema for Transaction
class TransactionBase(BaseModel):
    sender_account_id: UUID = Field(
        ...,
        description="Sender's Account ID"
    )
    receiver_account_id: UUID = Field(
        ...,
        description="Receiver's Account ID"
    )
    sender_username: str = Field(
        ...,
        description="Sender's username"
    )
    receiver_username: str = Field(
        ...,
        description="Receiver's username"
    )
    transfer_amount: float = Field(
        ...,
        description="Amount to be Transferred"
    )

    model_config = ConfigDict(from_attributes=True)


# Request Model for Money Transfer
class TransactionRequest(BaseModel):
    receiver_account_id: UUID = Field(
        ...,
        description="Receiver's Account ID"
    )
    receiver_username: str = Field(
        ...,
        description="Receiver's username"
    )
    transfer_amount: float = Field(
        ...,
        description="Amount to be Transferred"
    )

    model_config = ConfigDict(from_attributes=True)



# Response Model for Money Transfer
class TransactionResponse(TransactionBase):
    id: UUID = Field(
        ...,
        description="Transaction ID"
    )
    made_at: datetime = Field(
        ...,
        description="Timestamp when the transaction occurred"
    )
    status: ValidTransactionStatus = Field(
        ...,
        description="Current status of the transaction"
    )


class SubscriptionBase(BaseModel):
    user_id: UUID = Field(
        ...,
        description="ID of the user who owns the Subscription"
    )
    source_id: Optional[str] = Field(
        None,
        description="Stripe Source ID (if any)"
    )
    currency: Optional[str] = Field(
        None,
        description="Currency Type of the Subscription"
    )
    amount: Optional[float] = Field(
        None,
        description="Amount charged for the subscription"
    )
    started_at: Optional[datetime] = Field(
        None,
        description="Subscription Start Time"
    )
    ended_at: Optional[datetime] = Field(
        None,
        description="Subscription End Time"
    )
    canceled_at: Optional[datetime] = Field(
        None,
        description="Time at which the Subscription was Cancelled"
    )
    status: ValidSubscriptionStatus = Field(
        ...,
        description="Current Status of the Subscription"
    )

    model_config = ConfigDict(from_attributes=True)


class SubscriptionResponse(SubscriptionBase):
    id: UUID = Field(
        ...,
        description="Subscription ID"
    )


class UpdateSubscriptionRequest(BaseModel):
    status: ValidSubscriptionStatus = Field(
        ...,
        description="Updated Status of the Subscription"
    )
