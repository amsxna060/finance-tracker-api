"""
Database models package.
Imports all SQLAlchemy models to ensure they are registered with the Base.
"""

from .user import User

# Import other models here as they are created
# from .account import Account
# from .category import Category  
# from .transaction import Transaction

__all__ = ["User"]
