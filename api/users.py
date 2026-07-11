from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pwdlib import PasswordHasher
from db.database import get_db
from models.models import User
from Schemas.schemas import UserBase, UserOut
from repositories.user_repo import UserRepo

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserBase, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepo(db)
    
    user = await user_repo.get_user_by_email(payload.email)

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hasher = PasswordHasher()
    hashed_password = password_hasher.hash(payload.password)

    user = await user_repo.create_user(email=payload.email, username=payload.username, hashed_password=hashed_password)
    
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepo(db)
    user = await user_repo.get_user_by_id(user_id)  
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserOut])
async def list_users(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
