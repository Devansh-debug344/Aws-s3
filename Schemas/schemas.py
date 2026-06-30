from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from fastapi import UploadFile


# User Schemas 
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# Item Schemas 
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemOut(ItemBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class BucketItem(BaseModel):
    owner_id : int
    text : Optional[str] = None
     
class BucketItemOut(BucketItem):
     id : int
     owner_id : int
     created_at: datetime

     model_config = {"from_attributes": True}

class Object_Out(BaseModel):
    id : int 
    key : Optional[str] = None
    file : Optional[UploadFile] = None
    bucket_id : int
    size : int
    created_at : datetime

    model_config = {"from_attributes": True}

