from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from validations.roles import (
    RoleRequest,
    RoleResponse,
    RoleUpdateRequest,
    RoleDeleteRequest)
from utils.db import db_dependency
from schemas.roles import Role
from utils.auth import require_role
from sqlalchemy.future import select


router = APIRouter()


@router.post("/role/add", response_model=List[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(roles: List[RoleRequest],
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(require_role(3))]):
    """Create a New Role."""
    try:
        new_roles = [Role(**role.model_dump()) for role in roles]
        db.add_all(new_roles)

        await db.commit()
        return [RoleResponse.model_validate(new_role) for new_role in new_roles]
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Creating Roles: {str(e)}")



@router.get("/role/all", response_model=List[RoleResponse], status_code=status.HTTP_200_OK)
async def get_roles(db: db_dependency):
    """Get Roles Details along with their Associated IDs."""
    try:
        stmt = select(Role)
        result = await db.execute(stmt)
        roles = result.scalars().all()
        return [RoleResponse.model_validate(role) for role in roles]
    
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Role: {str(e)}")



@router.put("/role/mod/", response_model=List[RoleResponse], status_code=status.HTTP_202_ACCEPTED)
async def update_role(updated_data: List[RoleUpdateRequest], 
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(require_role(3))]):
    """Update Existing Roles."""
    try:
        roles_to_update = {role.id: role for role in updated_data}
        stmt = select(Role).where(Role.id.in_(roles_to_update))
        result = await db.execute(stmt)
        roles = result.scalars().all()

        for role in roles:
            updated_role = roles_to_update.get(role.id, None)
            if not updated_role:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Role Not Found for Level: {role.level}")
            
            if updated_role.level is not None:
                role.level = updated_role.level
                
            if updated_role.position is not None:
                role.position = updated_role.position

        await db.commit()
        response = []
        for role in roles:
            await db.refresh(role)
            response.append(RoleResponse.model_validate(role))

        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Updating Role: {str(e)}")



@router.delete("/role/del", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(roles_for_deletion: List[RoleDeleteRequest],
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(require_role(3))]):
    """Delete Roles, Can be Done only by Admin Account."""
    try:
        role_ids_to_delete = [role.id for role in roles_for_deletion]
        stmt = select(Role).where(Role.id.in_(role_ids_to_delete))
        result = await db.execute(stmt)
        roles_to_delete = result.scalars().all()

        if not roles_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Roles Not Found")
            
        for role in roles_to_delete:
            db.delete(role)
            
        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Role: {str(e)}")