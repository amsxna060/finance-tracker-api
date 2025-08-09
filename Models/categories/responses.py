"""
Category-related response models (Pydantic models for API output)
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from database.models.category import CategoryType


class CategoryResponse(BaseModel):
    """Response model for category data"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    category_type: CategoryType
    icon: Optional[str]
    is_system_category: bool
    created_at: datetime
    updated_at: datetime


class UserCategoryResponse(BaseModel):
    """Response model for user's personalized category view"""
    id: int
    name: str  # Original category name
    custom_name: Optional[str]  # User's custom name
    description: Optional[str]
    category_type: CategoryType
    icon: Optional[str]
    is_active: bool
    is_system_category: bool
    assigned_at: datetime  # When user added this category


class CategorySummaryResponse(BaseModel):
    """Response model for category usage statistics"""
    category_id: int
    category_name: str
    category_type: CategoryType
    transaction_count: int
    total_amount: float
    last_used: Optional[datetime]
