from fastapi import APIRouter, status, HTTPException, Query
from utils.db import db_dependency
from validations.users import (
    Token,
    UserPublicResponse,
    UserRead,
    UserRequest
)
from utils.auth import (
    bcrypt_context,
    auth_form,
    authenticate_user,
    create_access_token,
    user_dependency,
)
from datetime import timedelta
from schemas.roles import Role, ValidRoles
from schemas.users import User
from sqlalchemy.future import select


router = APIRouter(prefix="/auth")


@router.get("/me", response_model=UserPublicResponse, status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could Not Validate User")

        return UserPublicResponse(
            id=user["id"],
            username=user["username"],
            role=user["role"]
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching User: {str(e)}")


@router.post("/login", response_model=Token, status_code=status.HTTP_202_ACCEPTED)
async def user_login(form_data: auth_form, db: db_dependency, mode: str = Query(...)):
    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could Not Validate User")

        if user.role.position != mode:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid Credentials or Mode")

        token = create_access_token(username=user.username,
                                    user_id=user.id,
                                    role=user.role.position,
                                    expires_in=timedelta(minutes=30))
        return Token(access_token=token, token_type="bearer")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Login Failed: {str(e)}")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserRequest, db: db_dependency):
    """Add a New User with Access Level 1."""
    try:
        stmt = select(Role).where(Role.level == 1)
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=bcrypt_context.hash(user_data.password),
            role_id=role.id)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return UserRead.model_validate(new_user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Creating Public User: {str(e)}")
