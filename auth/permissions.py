from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import User as DBUser
from database.models.user import Role
from Models.UserResponse import UserResponse
from util import verify_token

# Security scheme for token extraction
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    Dependency to get current user from JWT token with role information
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Extract user information from token
    user_email = payload.get("email")
    user_role = payload.get("role")
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Find user by email from token
    user = db.query(DBUser).filter(DBUser.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify role matches what's in database (security check)
    if user.role.value != user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token role mismatch"
        )
    
    return UserResponse.model_validate(user)

def require_auth(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependency that requires authentication (any authenticated user)
    """
    return current_user

def require_role(required_role: str):
    """
    Decorator factory that creates a dependency requiring a specific role
    """
    def role_dependency(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role.value != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
def require_role(required_role: Role):
    """
    Decorator factory that creates a dependency requiring a specific role
    """
    def role_dependency(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}"
            )
        return current_user
    
    return role_dependency

def require_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependency that requires admin role
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required"
        )
    return current_user