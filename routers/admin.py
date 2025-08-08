from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from Models.AccountResponse import AccountResponse
from database.session import get_db
from database.models import User as DBUser
from database.models import Account as DBAccount
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

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only)
    """
    # Find the user to delete
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {"detail": "User deleted successfully"}

# Admin can see all accounts from all users
@router.get('/accounts', response_model=List[AccountResponse])
async def get_all_accounts_admin(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    accounts = db.query(DBAccount).all()
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No accounts found"
        )
    return [AccountResponse.model_validate(account) for account in accounts]

@router.get('/accounts/{user_id}', response_model=List[AccountResponse])
async def get_account_admin(user_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """
    Get all accounts for a specific user (admin only)
    """
    # Find user by ID
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get accounts for the user
    accounts = db.query(DBAccount).filter(DBAccount.user_id == user_id).all()
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No accounts found for this user"
        )
    
    return [AccountResponse.model_validate(account) for account in accounts]