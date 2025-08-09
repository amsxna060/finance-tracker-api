"""
Models package - Clean imports for all Pydantic models
Organized by domain for better maintainability and scalability
"""

# User models
from .users import (
    UserCreateRequest,
    LoginRequest,
    UserUpdateRequest,
    UserResponse,
    LoginResponse
)

# Account models
from .accounts import (
    AccountCreateRequest,
    AccountUpdateRequest,
    AccountResponse,
    AccountBalanceResponse
)

# Category models
from .categories import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    UserCategoryAssignRequest,
    CategoryResponse,
    UserCategoryResponse,
    CategorySummaryResponse
)

# Transaction models - Ready for Day 7
from .transactions import (
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    TransactionSummaryResponse
)

__all__ = [
    # User models
    'UserCreateRequest',
    'LoginRequest',
    'UserUpdateRequest',
    'UserResponse',
    'LoginResponse',
    
    # Account models
    'AccountCreateRequest',
    'AccountUpdateRequest',
    'AccountResponse',
    'AccountBalanceResponse',
    
    # Category models
    'CategoryCreateRequest',
    'CategoryUpdateRequest',
    'UserCategoryAssignRequest',
    'CategoryResponse',
    'UserCategoryResponse',
    'CategorySummaryResponse',
    
    # Transaction models - will be added in Day 7
    'TransactionCreateRequest',
    'TransactionUpdateRequest',
    'TransactionResponse',
    'TransactionSummaryResponse'
]
