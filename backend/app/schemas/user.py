from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    is_active: bool = Field(default=True, description="Whether the user is active")
    is_superuser: bool = Field(default=False, description="Whether the user is a superuser")

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., description="User's password", min_length=8)

class UserResponse(UserBase):
    """Schema for user response including database fields."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM mode 