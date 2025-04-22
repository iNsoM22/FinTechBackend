from uuid import UUID
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from schemas.accounts import ValidAccountStatus
from schemas.transactions import ValidTransactionStatus


# Base Schema for Account
class AccountBase(BaseModel):
    user_id: int = Field(
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


# Response Model with Transactions
class AccountResponseWithTransactions(AccountResponse):
    sent_transactions: List["TransactionResponseLite"] = Field(
        default_factory=list, description="List of Sent Transactions"
    )
    received_transactions: List["TransactionResponseLite"] = Field(
        default_factory=list, description="List of Received Transactions"
    )


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
class TransactionRequest(TransactionBase):
    pass


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