from fastapi import APIRouter, status, HTTPException, Query
from utils.db import db_dependency
from utils.auth import user_dependency
from validations.accounts import (
    AccountUpdateRequest, TransactionRequest, AccountResponse, TransactionResponse, AccountBalanceResponse)
from schemas.accounts import Account
from schemas.transactions import Transaction, ValidTransactionStatus
from sqlalchemy.future import select
from sqlalchemy import or_
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional


router = APIRouter(prefix="/accounts")


# Update Account
@router.put("/{account_id}", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def update_account(account_id: UUID,
                         account_update: AccountUpdateRequest,
                         db: db_dependency,
                         current_user: user_dependency):
    try:
        stmt = select(Account).where(Account.id == account_id,
                                     Account.user_id == current_user["id"])
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account Not Found")

        if account_update.currency is not None:
            account.currency = account_update.currency
        if account_update.status is not None:
            account.status = account_update.status

        await db.commit()
        await db.refresh(account)

        return AccountResponse.model_validate(account)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Account: {str(e)}")


# Transfer Money
@router.post("/transfer", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def transfer_money(transfer_data: TransactionRequest,
                         db: db_dependency,
                         current_user: user_dependency):
    try:
        stmt_sender = select(Account).where(Account.user_id == current_user["id"])
        result_sender = await db.execute(stmt_sender)
        sender = result_sender.scalar_one_or_none()

        if not sender or sender.balance < transfer_data.transfer_amount:
            raise HTTPException(
                400, detail="Insufficient Balance or Invalid Sender Account")

        stmt_receiver = select(Account).where(
            Account.id == transfer_data.receiver_account_id)
        result_receiver = await db.execute(stmt_receiver)
        receiver = result_receiver.scalar_one_or_none()
        if not receiver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Receiver Account Not Found")

        transaction = Transaction(
            sender_account_id=sender.id,
            receiver_account_id=receiver.id,
            transfer_amount=transfer_data.transfer_amount,
            made_at=datetime.now(timezone.utc),
            status=ValidTransactionStatus.COMPLETED
        )

        sender.balance -= transfer_data.transfer_amount
        receiver.balance += transfer_data.transfer_amount

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return TransactionResponse(id=transaction.id,
                                   receiver_account_id=transaction.receiver_account_id,
                                   sender_account_id=transaction.sender_account_id,
                                   receiver_username=transfer_data.receiver_username,
                                   sender_username=current_user["username"],
                                   made_at=transaction.made_at,
                                   status=transaction.status,
                                   transfer_amount=transaction.transfer_amount)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Processing Transfer: {str(e)}")


# Get Transaction History
@router.get("/{account_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
async def get_transactions(account_id: UUID,
                           db: db_dependency,
                           current_user: user_dependency,
                           limit: int = Query(50, ge=1, le=100),
                           offset: int = Query(0, ge=0),
                           date_from: Optional[datetime] = Query(None),
                           date_till: Optional[datetime] = Query(None)):
    try:
        stmt = select(Account).where(Account.id == account_id,
                                     Account.user_id == current_user["id"])
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account Not Found")

        stmt_tx = select(Transaction).where(
            or_(
                Transaction.sender_account_id == account_id,
                Transaction.receiver_account_id == account_id
            )
        )

        if date_from:
            stmt_tx = stmt_tx.where(Transaction.made_at >= date_from)
        if date_till:
            stmt_tx = stmt_tx.where(Transaction.made_at <= date_till)

        stmt_tx = stmt_tx.order_by(
            Transaction.made_at.desc()).offset(offset).limit(limit)

        result_tx = await db.execute(stmt_tx)
        transactions = result_tx.scalars().all()

        return [TransactionResponse.model_validate(t) for t in transactions]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Transactions: {str(e)}")


# Get Current Account Details
@router.get("/{account_id}", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def get_account_details(account_id: UUID,
                              db: db_dependency,
                              current_user: user_dependency):
    try:
        stmt = select(Account).where(Account.id == account_id,
                                     Account.user_id == current_user["id"])
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account Not Found")

        return AccountResponse.model_validate(account)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Account Details: {str(e)}")


# Get Current Account Balance
@router.get("/balance/me", response_model=AccountBalanceResponse, status_code=status.HTTP_200_OK)
async def get_balance(db: db_dependency, current_user: user_dependency):
    try:
        stmt = select(Account).where(Account.user_id == current_user["id"])
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Account Not Found")

        return AccountBalanceResponse.model_validate(account)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Account Details: {str(e)}")
