from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


# Token Model for User Authentication (JWT)
class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="User Access Token for JWT"
    )
    token_type: str = Field(
        ...,
        description="Type of the Token"
    )


# Base User Model for User Account Record
class UserBase(BaseModel):
    username: str = Field(
        min_length=7,
        max_length=20,
        description="Username to be used in the Account"
    )
    level: int = Field(
        default=1,
        description="Role Level of the User (Requires Special Privileges to Use a High Level)"
    )

    model_config = ConfigDict(from_attributes=True)


# Request Model for User Account Creation (includes email and password)
class UserRequest(UserBase):
    email: EmailStr = Field(
        max_length=40,
        description="Email of the User"
    )
    password: str = Field(
        min_length=9,
        max_length=100,
        description="Password for the User Account"
    )


# Request Model for User Account Login (can use either Username or Email)
class UserLoginRequest(BaseModel):
    username: Optional[str] = Field(
        min_length=7,
        max_length=20,
        example="Username used in the Account"
    )
    email: Optional[EmailStr] = Field(
        max_length=40,
        description="Email of the User"
    )
    password: str = Field(
        min_length=9,
        max_length=100,
        description="Password used in the Account"
    )


# Public Update Request Model (change Username, Email, Password)
# Would be Used, if the User is Changing their Account Information
class UserPublicUpdateRequest(BaseModel):
    new_username: Optional[str] = Field(
        min_length=7,
        max_length=20,
        example="New Username to be used in the Account"
    )
    new_email: Optional[EmailStr] = Field(
        max_length=40,
        example="New Email to be used in the Account"
    )
    new_password: Optional[str] = Field(
        min_length=9,
        max_length=100,
        description="New Password for the User Account"
    )


# User Read Model, Used When Retrieving User Record
class UserRead(UserBase):
    id: UUID = Field(
        ...,
        description="Unique Identifier for the User"
    )
    email: EmailStr = Field(
        max_length=40,
        description="Email of the User"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the User was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the User was last updated"
    )


# Public User Response, used for Returning User Data without any Sensitive Information
class UserPublicResponse(UserBase):
    id: UUID = Field(
        ...,
        description="Unique Identifier for the User"
    )
    email: EmailStr = Field(
        max_length=40,
        description="Email of the User"
    )
