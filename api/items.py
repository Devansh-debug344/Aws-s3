from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from models.models import Item
from Schemas.schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    owner_id: int,          # replace with actual auth dependency in production
    db: AsyncSession = Depends(get_db),
):
    item = Item(**payload.model_dump(), owner_id=owner_id)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/", response_model=list[ItemOut])
async def list_items(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).offset(skip).limit(limit))
    return result.scalars().all()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(item)
