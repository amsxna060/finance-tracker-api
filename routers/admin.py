from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.session import get_db
from database.models import User as DBUser
from database.models.user import Role
from Models.UserResponse import UserResponse
from auth.permissions import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)]
)

class RoleUpdate(BaseModel):
    role: Role

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users in the system (admin only)
    """
    users = db.query(DBUser).all()
    return [UserResponse.model_validate(user) for user in users]

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role (admin only)
    """
    # Find the user to update
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update the user's role
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)