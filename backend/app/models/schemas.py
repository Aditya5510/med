# backend/app/models/schemas.py

from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from bson import ObjectId


# ============================
# USER & AUTH SCHEMAS
# ============================

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str    # will receive MongoDB’s "_id" as a string
    hashed_password: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str  # e.g., "bearer"

class TokenData(BaseModel):
    username: Optional[str]

class LoginRequest(BaseModel):
    username: str
    password: str


# ============================
# HEALTH PROFILE SCHEMAS
# ============================

class HealthProfileBase(BaseModel):
    age: int
    gender: str
    weight: float
    height: float
    dietary_preferences: Optional[List[str]]
    existing_conditions: Optional[List[str]]

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileInDB(HealthProfileBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HealthProfileResponse(HealthProfileBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================
# MEAL PLAN SCHEMAS
# ============================

class MealPlanDay(BaseModel):
    day: int
    meals: Dict[str, str]  # e.g., {"breakfast": "Oatmeal", "lunch": "Salad", ...}

class MealPlanResponse(BaseModel):
    calorie_target: float
    days: List[MealPlanDay]

    model_config = ConfigDict(from_attributes=True)


# ============================
# WORKOUT PLAN SCHEMAS
# ============================

class ExerciseItem(BaseModel):
    name: str
    reps: Optional[str]
    duration: Optional[str]

class WorkoutPlanDay(BaseModel):
    day: int
    exercises: List[ExerciseItem]

class WorkoutPlanResponse(BaseModel):
    days: List[WorkoutPlanDay]

    model_config = ConfigDict(from_attributes=True)


# ============================
# RECIPE SCHEMAS
# ============================

class NutritionInfo(BaseModel):
    calories: int
    protein: int  # grams
    fat: int      # grams
    carbs: int    # grams

class RecipeResponse(BaseModel):
    meal_name: str
    ingredients: List[str]
    instructions: str
    nutrition: NutritionInfo

    model_config = ConfigDict(from_attributes=True)


# ============================
# PROGRESS TRACKER SCHEMAS
# ============================

class DailyLogBase(BaseModel):
    date: str            # ISO date string, e.g. "2025-06-01"
    weight: float
    calories_in: int
    calories_out: int

class DailyLogCreate(DailyLogBase):
    pass

class DailyLogInDB(DailyLogBase):
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DailyLogResponse(DailyLogBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProgressSummary(BaseModel):
    first_log_date: str  # ISO date string
    first_weight: float
    last_log_date: str   # ISO date string
    last_weight: float
    weight_change: float  # last_weight - first_weight

    model_config = ConfigDict(from_attributes=True)
