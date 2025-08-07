from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .category import user_category_association


import enum

class Gender(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class Role(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    gender = Column(Enum(Gender),default=Gender.MALE)  
    password = Column(String)  # Will store hashed password
    age = Column(Integer, nullable = True)
    role = Column(Enum(Role), default=Role.USER)  # Add role field with default 'user'
    is_verified = Column(Boolean, default=False)
    currency = Column(String, default="USD")
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship declarations will go here later
    accounts = relationship("Account", back_populates="user")
    categories = relationship("Category", secondary=user_category_association, back_populates="users")
    transactions = relationship("Transaction", back_populates="user")
    
