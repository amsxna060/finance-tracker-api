"""
Category router - CRUD operations for categories
Handles both system categories (admin) and user category assignments
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import get_db
from database.models.category import Category as DBCategory, user_category_association
from database.models import User as DBUser
from Models.categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    UserCategoryAssignRequest,
    CategoryResponse,
    UserCategoryResponse,
    CategorySummaryResponse
)
from auth.permissions import require_auth, get_current_user, require_admin
from sqlalchemy import select, and_

router = APIRouter(
    prefix='/categories',
    tags=['Categories'],
    dependencies=[Depends(require_auth)]
)

# =============================================================================
# SYSTEM CATEGORIES (Admin Only)
# =============================================================================

@router.post('/system/create', response_model=CategoryResponse)
async def create_system_category(
    category: CategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Create a new system category (admin only)"""
    # Check if category name already exists
    existing = db.query(DBCategory).filter(DBCategory.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category.name}' already exists"
        )
    
    # Create new system category
    new_category = DBCategory(
        name=category.name,
        description=category.description,
        category_type=category.category_type,
        icon=category.icon,
        is_system_category=True
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse.model_validate(new_category)


@router.get('/system', response_model=List[CategoryResponse])
async def get_all_system_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all available system categories"""
    categories = db.query(DBCategory).filter(DBCategory.is_system_category == True).all()
    return [CategoryResponse.model_validate(cat) for cat in categories]


@router.put('/system/{category_id}', response_model=CategoryResponse)
async def update_system_category(
    category_id: int,
    category_update: CategoryUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Update a system category (admin only)"""
    category = db.query(DBCategory).filter(
        DBCategory.id == category_id,
        DBCategory.is_system_category == True
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System category not found"
        )
    
    # Update only provided fields
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return CategoryResponse.model_validate(category)


# =============================================================================
# USER CATEGORIES (User's Personal Category Management)
# =============================================================================

@router.get('/my', response_model=List[UserCategoryResponse])
async def get_my_categories(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get current user's categories (both assigned and custom)"""
    # Complex query to get user's categories with custom names
    query = db.query(
        DBCategory,
        user_category_association.c.custom_name,
        user_category_association.c.is_active,
        user_category_association.c.created_at.label('assigned_at')
    ).join(
        user_category_association,
        DBCategory.id == user_category_association.c.category_id
    ).filter(
        user_category_association.c.user_id == current_user.id,
        user_category_association.c.is_active == True
    ).all()
    
    user_categories = []
    for category, custom_name, is_active, assigned_at in query:
        user_cat = UserCategoryResponse(
            id=category.id,
            name=category.name,
            custom_name=custom_name,
            description=category.description,
            category_type=category.category_type,
            icon=category.icon,
            is_active=is_active,
            is_system_category=category.is_system_category,
            assigned_at=assigned_at
        )
        user_categories.append(user_cat)
    
    return user_categories


@router.post('/assign', response_model=UserCategoryResponse)
async def assign_category_to_user(
    assignment: UserCategoryAssignRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign a system category to current user"""
    # Check if category exists
    category = db.query(DBCategory).filter(DBCategory.id == assignment.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if already assigned
    existing = db.query(user_category_association).filter(
        and_(
            user_category_association.c.user_id == current_user.id,
            user_category_association.c.category_id == assignment.category_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already assigned to user"
        )
    
    # Create assignment
    stmt = user_category_association.insert().values(
        user_id=current_user.id,
        category_id=assignment.category_id,
        custom_name=assignment.custom_name,
        is_active=assignment.is_active
    )
    db.execute(stmt)
    db.commit()
    
    # Return the user category response
    return UserCategoryResponse(
        id=category.id,
        name=category.name,
        custom_name=assignment.custom_name,
        description=category.description,
        category_type=category.category_type,
        icon=category.icon,
        is_active=assignment.is_active,
        is_system_category=category.is_system_category,
        assigned_at=db.query(user_category_association.c.created_at).filter(
            and_(
                user_category_association.c.user_id == current_user.id,
                user_category_association.c.category_id == assignment.category_id
            )
        ).scalar()
    )


@router.put('/my/{category_id}', response_model=UserCategoryResponse)
async def update_my_category(
    category_id: int,
    update_req: UserCategoryAssignRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user's category assignment (custom name, active status)"""
    # Check if user has this category assigned
    assignment = db.query(user_category_association).filter(
        and_(
            user_category_association.c.user_id == current_user.id,
            user_category_association.c.category_id == category_id
        )
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not assigned to user"
        )
    
    # Update assignment
    stmt = user_category_association.update().where(
        and_(
            user_category_association.c.user_id == current_user.id,
            user_category_association.c.category_id == category_id
        )
    ).values(
        custom_name=update_req.custom_name,
        is_active=update_req.is_active
    )
    db.execute(stmt)
    db.commit()
    
    # Get category details for response
    category = db.query(DBCategory).filter(DBCategory.id == category_id).first()
    
    return UserCategoryResponse(
        id=category.id,
        name=category.name,
        custom_name=update_req.custom_name,
        description=category.description,
        category_type=category.category_type,
        icon=category.icon,
        is_active=update_req.is_active,
        is_system_category=category.is_system_category,
        assigned_at=assignment.created_at
    )


@router.delete('/my/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_my_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove category from user's list (sets inactive)"""
    # Update to inactive instead of deleting
    stmt = user_category_association.update().where(
        and_(
            user_category_association.c.user_id == current_user.id,
            user_category_association.c.category_id == category_id
        )
    ).values(is_active=False)
    
    result = db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category assignment not found"
        )
    
    db.commit()
    return {"detail": "Category removed from your list"}
