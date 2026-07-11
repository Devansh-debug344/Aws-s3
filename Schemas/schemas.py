from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from fastapi import UploadFile


# User Schemas 
class UserBase(BaseModel):
    email: EmailStr
    username: str
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
    bucket_name : str
    text : Optional[str] = None
     
class BucketItemOut(BucketItem):
     name : str
     owner_id : int

     model_config = {"from_attributes": True}

class Object_Out(BaseModel):
    bucket_id : int
    object_name : Optional[str] = None
    size : Optional[int] = None
    etag : Optional[str] = None
    storage_path : Optional[str] = None
    created_at : datetime
    response_url : Optional[str] = None

    model_config = {"from_attributes": True}

