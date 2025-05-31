from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# USER SCHEMAS

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str  

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
