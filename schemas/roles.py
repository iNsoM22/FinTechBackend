from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Enum as SQLAEnum
from .base import Base
from enum import Enum as PEnum


# Valid Roles to be Supported by the System
class ValidRoles(str, PEnum):
    USER = "User"
    DEVELOPER = "Developer"
    ADMIN = "Admin"


# Schema for Roles Table (Will be Used for RBAC)
class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Surrogate Key for the Roles."
    )

    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
        comment="Role Level of the Access."
    )

    position: Mapped[ValidRoles] = mapped_column(
        SQLAEnum(ValidRoles, name="valid_roles"),
        nullable=False,
        unique=True,
        comment="Named Role Position for the Access."
    )
