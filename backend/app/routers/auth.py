# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson.objectid import ObjectId

from ..dependencies import get_database, settings
from ..models.schemas import (
    UserCreate,
    UserInDB,
    UserResponse,
    Token,
    TokenData,
    LoginRequest
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[UserInDB]:
    row = await db["users"].find_one({"username": username})
    if row:
        return UserInDB(**row)
    return None

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
    row = await db["users"].find_one({"email": email})
    if row:
        return UserInDB(**row)
    return None

async def authenticate_user(db: AsyncIOMotorDatabase, username: str, password: str) -> Optional[UserInDB]:
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    
    if await db["users"].find_one({"username": user_in.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await db["users"].find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

   
    hashed_password = get_password_hash(user_in.password)
    user_doc = {
        "username": user_in.username,
        "email": user_in.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }
    result = await db["users"].insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    return UserResponse(
        id=str(user_doc["_id"]),
        username=user_doc["username"],
        email=user_doc["email"],
        created_at=user_doc["created_at"]
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
  
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

   
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Protected endpoint: returns the currently authenticated user.
    """
    return UserResponse(
        id=str(current_user.__dict__.get("_id", "")) or "",
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at
    )
