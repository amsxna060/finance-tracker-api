from sqlalchemy import Boolean, Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
from sqlalchemy.types import Enum 
import enum

class CategoryType(enum.Enum):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'

# 🌉 THE BRIDGE TABLE - This is the magic connector!
user_category_association = Table(
    'user_categories',                    # Table name in database
    Base.metadata,                        # Tell SQLAlchemy about this table
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),      # Points to User
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True), # Points to Category
    Column('is_active', Boolean, default=True),        # User can hide categories
    Column('custom_name', String, nullable=True),      # User can rename "Food" to "Meals"
    Column('created_at', DateTime, default=func.now()) # When user added this category
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # 🔥 UNIQUE! Only one "Food" category globally
    description = Column(String, nullable=True)
    category_type = Column(Enum(CategoryType), default=CategoryType.EXPENSE)
    icon = Column(String, nullable=True)  # 🍕, ⛽, 🎬 for pretty UI
    is_system_category = Column(Boolean, default=True)  # Admin vs user created
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 🔥 THE MAGIC LINE - Many-to-Many relationship
    users = relationship("User", secondary=user_category_association, back_populates="categories")
    transactions = relationship("Transaction", back_populates="category") 
