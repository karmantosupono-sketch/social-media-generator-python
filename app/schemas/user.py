from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str 

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True 