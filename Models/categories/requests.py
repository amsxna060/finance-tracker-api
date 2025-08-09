"""
Category-related request models (Pydantic models for API input validation)
"""
from pydantic import BaseModel, Field
from typing import Optional
from database.models.category import CategoryType


class CategoryCreateRequest(BaseModel):
    """Request model for creating a new category"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    category_type: CategoryType = CategoryType.EXPENSE
    icon: Optional[str] = Field(None, max_length=10)  # Emoji or icon code


class CategoryUpdateRequest(BaseModel):
    """Request model for updating an existing category (partial updates)"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    category_type: Optional[CategoryType] = None
    icon: Optional[str] = Field(None, max_length=10)


class UserCategoryAssignRequest(BaseModel):
    """Request model for assigning categories to users"""
    category_id: int
    custom_name: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
