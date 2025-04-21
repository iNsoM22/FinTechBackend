from fastapi import APIRouter, status, HTTPException, Depends
from utils.db import db_dependency
from validations.users import (
    UserRequest,
    UserRead,
    UserPublicUpdateRequest
)
from utils.auth import (
    bcrypt_context,
    require_role,
    user_dependency
)
from schemas.users import User
from typing import Annotated, List
from uuid import UUID
from sqlalchemy.future import select

router = APIRouter(prefix="/user")


@router.post("/admin/add", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_internal_user(user_data: UserRequest,
                               db: db_dependency):
    """Add a New User with Certain Access Levels (Internal Use Only)."""
    try:
        if not user_data.role_id in [1, 2, 3]:
            raise

        new_user = User(
            username=user_data.username,
            password=bcrypt_context.hash(user_data.password),
            email=user_data.email,
            role_id=user_data.role_id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return UserRead.model_validate(new_user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Creating Internal User: {str(e)}")


@router.get("/get/{identifier}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user_from_identifier(identifier: str | UUID,
                                   db: db_dependency,
                                   current_user: user_dependency,
                                   from_username: bool = False,
                                   from_email: bool = False):
    """Usage and Purpose of this API End-Point will be Resolved Later."""
    try:
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could Not Validate User")

        stmt = select(User)
        if from_username:
            stmt = stmt.where(User.username == identifier)
        elif from_email:
            stmt = stmt.where(User.email == identifier)
        else:
            stmt = stmt.where(User.id == identifier)

        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Not Found")

        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching User: {str(e)}")


@router.get("/all", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency,
                        current_user: Annotated[dict, Depends(require_role(2))],
                        limit: int = 50,
                        offset: int = 0):
    try:
        stmt = select(User).offset(offset).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return [UserRead.model_validate(user) for user in users]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Users Records: {str(e)}")


@router.put("/mod", response_model=UserRead, status_code=status.HTTP_202_ACCEPTED)
async def modify_user(updated_user: UserPublicUpdateRequest,
                      db: db_dependency,
                      current_user: user_dependency):
    """Modify Details of the Current Authenticated User."""
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )

        stmt = select(User).where(
            User.id == current_user["id"], User.username == current_user["username"])
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )

        if updated_user.new_username is not None:
            user.username = updated_user.new_username
        if updated_user.new_password is not None:
            user.password = bcrypt_context.hash(updated_user.new_password)
        if updated_user.new_email is not None:
            user.email = updated_user.new_email

        await db.commit()
        await db.refresh(user)
        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Modifying User: {str(e)}")
