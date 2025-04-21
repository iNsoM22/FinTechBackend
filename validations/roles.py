from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from schemas.roles import ValidRoles


# Base Schema for Role Model
class RoleBase(BaseModel):
    level: int = Field(
        ...,
        description="Role Level for Role Based Access Control"
    )
    position: ValidRoles = Field(
        ...,
        description="Name of the Role from Valid Roles"
    )

    model_config = ConfigDict(from_attributes=True)


# Request Model for Role Creation
class RoleRequest(RoleBase):
    pass


# Request Model for Role Updation
class RoleUpdateRequest(BaseModel):
    level: Optional[int] = Field(
        None,
        description="Updated Role Level"
    )
    position: Optional[ValidRoles] = Field(
        None,
        description="Updated Role Position Name"
    )

    model_config = ConfigDict(from_attributes=True)


# Request Model for Role Deletion
class RoleDeleteRequest(BaseModel):
    id: int = Field(
        ...,
        description="Role ID to delete"
    )


# Response Model for Role
class RoleResponse(RoleBase):
    id: int = Field(
        ...,
        description="Unique Role ID"
    )


# Response Model for Role With Linked Users (for future use)
class RoleResponseWithUsers(RoleResponse):
    pass
