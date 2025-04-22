from fastapi import APIRouter, status, HTTPException, Query, Depends
from utils.db import db_dependency
from utils.auth import user_dependency
from schemas.subscriptions import Subscription, ValidSubscriptionStatus
from validations.accounts import SubscriptionResponse, UpdateSubscriptionRequest
from sqlalchemy.future import select
from utils.auth import user_dependency, require_role
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Annotated


router = APIRouter(prefix="/subscriptions")


@router.get("/", response_model=List[SubscriptionResponse], status_code=status.HTTP_200_OK)
async def get_all_my_subscriptions(db: db_dependency, current_user: user_dependency):
    try:
        stmt = select(Subscription).where(
            Subscription.user_id == current_user["id"])
        result = await db.execute(stmt)
        subscriptions = result.scalars().all()
        return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Failed to Fetch Subscriptions: {str(e)}")


@router.put("/{subscription_id}", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
async def update_subscription(subscription_id: UUID,
                              updated_data: UpdateSubscriptionRequest,
                              db: db_dependency,
                              current_user: Annotated[dict, Depends(require_role(2))]):
    try:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscription Not Found")

        for field, value in updated_data.model_dump().items():
            setattr(subscription, field, value)

        await db.commit()
        await db.refresh(subscription)
        return SubscriptionResponse.model_validate(subscription)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Failed to Update Subscription: {str(e)}")


@router.get("/filter", response_model=List[SubscriptionResponse], status_code=status.HTTP_200_OK)
async def filter_subscriptions(db: db_dependency,
                               current_user: Annotated[dict, Depends(require_role(2))],
                               status: Optional[ValidSubscriptionStatus] = Query(None),
                               start_date: Optional[datetime] = Query(None),
                               end_date: Optional[datetime] = Query(None)):
    try:
        stmt = select(Subscription)

        if status or start_date or end_date:
            filters = []
            if status:
                filters.append(Subscription.status == status)

            if start_date:
                filters.append(Subscription.started_at >= start_date)

            if end_date:
                filters.append(Subscription.ended_at <= end_date)

            stmt = stmt.where(*filters)

        result = await db.execute(stmt)
        subscriptions = result.scalars().all()
        return [SubscriptionResponse.model_validate(sub) for sub in subscriptions]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Filtering Subscriptions: {str(e)}")


# Get Current Account Active Subscription Status
@router.get("/me", response_model=SubscriptionResponse, status_code=status.HTTP_200_OK)
async def get_active_subscription(db: db_dependency, current_user: user_dependency):
    try:
        stmt = select(Subscription).where(Subscription.user_id == current_user["id"],
                                          Subscription.status == ValidSubscriptionStatus.ACTIVE)
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscription Not Found")

        return SubscriptionResponse.model_validate(subscription)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Subscription Details: {str(e)}")