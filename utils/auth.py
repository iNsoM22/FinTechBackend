from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import re
from schemas.users import User
from uuid import UUID
from datetime import timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("HASHING_ALGORITHM")

ROLE_LEVELS = {
    "User": 0,
    "Developer": 1,
    "Admin": 2
}


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


auth_form = Annotated[OAuth2PasswordRequestForm, Depends()]

# Util Function for Email String Check
def is_email(value: str) -> bool:
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.fullmatch(email_pattern, value) is not None


# Util Function to Check Whether the User is registered in the Database or Not
async def authenticate_user(identifier: str, password: str, db: AsyncSession) -> Optional[User]:
    try:
        stmt = select(User)
        if is_email(identifier):
            stmt = stmt.where(User.email == identifier)
        else:
            stmt = stmt.where(User.username == identifier)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None

        if not bcrypt_context.verify(password, user.password):
            return None
        
        return user

    except Exception as e:
        return None


# Util Function to Provide Access Tokens to the Users When Signing 
def create_access_token(username: str, user_id: UUID, role: str, expires_in: timedelta) -> str:
    encode = {
        "sub": username,
        "id": str(user_id),
        "pos": role,
    }
    expires = datetime.now(timezone.utc) + expires_in
    encode["exp"] = expires
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


# Util Function to Decode the Token, for Current User Information
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("pos")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could Not Validate User")

        return {
            "username": username,
            "id": UUID(user_id),
            "role": role,
        }

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could Not Validate User")


# Util Function to Set Minimum Level Access Dependencies
def require_role(min_level: int):
    def role_dependency(user: Annotated[dict, Depends(get_current_user)]):
        if user["role"] is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User Role Information is Missing"
            )
        user_level = ROLE_LEVELS.get(user["role"])
        
        if user_level is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid Role Provided")

        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient Permissions, Requires Higher Level Privelledges"
            )
        return user
    
    return role_dependency


# Validated User Dependency Injection for Routes
user_dependency = Annotated[dict, Depends(get_current_user)]