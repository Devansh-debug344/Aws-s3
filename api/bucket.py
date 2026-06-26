from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from Schemas.schemas import BucketItem , BucketItemOut , Object_Out
from db.database import get_db
from models.bucket import Bucket , Object
from sqlalchemy import select
import os
router = APIRouter(prefix="/buckets", tags=["Bucket"])

#create a bucket
@router.post("/create_bucket" , response_model = BucketItemOut , status_code=status.HTTP_201_CREATED)
async def create_bucket( payload : BucketItem , db : AsyncSession = Depends(get_db)):
     owner_id = payload.owner_id
     res = await db.execute(select(Bucket).where(owner_id == Bucket.owner_id))
     existng = res.scalar_one_or_none()
     if existng:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket for this user already existed !!!")
     
     bucket = Bucket(owner_id = owner_id)
     db.add(bucket)
     await db.flush()
     await db.refresh(bucket)
     return bucket
#post item in bucket
@router.post("/" , response_model = Object_Out , status_code=status.HTTP_201_CREATED)
async def add_item_bucket(payload : BucketItem , db : AsyncSession = Depends(get_db)):
        
       owner_id = payload.owner_id

       result = await db.execute(select(Bucket).where(Bucket.owner_id == owner_id))
       
       bucket = result.scalar_one_or_none()

       if not bucket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")
       
       obj = Object(key = payload.text , bucket_id = bucket.id, size = len(payload.text))
       db.add(obj)
       await db.flush()
       await db.refresh(obj)
       return obj

#get all the elements in bucket               

@router.get("/{owner_id}" , response_model=list[Object_Out] , status_code=status.HTTP_200_OK)
# or just remove it, 200 is the default for GET)
async def get_bucket_items(owner_id : int , db : AsyncSession = Depends(get_db)):

     result = await db.execute(select(Bucket).where(Bucket.owner_id == owner_id))
 
     bucket = result.scalar_one_or_none()

     bucket_id = bucket.id

     query = await db.execute(select(Object).where(Object.bucket_id == bucket_id))

     res = query.scalars().all()

     if not res:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")
     
     return res
         

@router.get("/{owner_id}/{txt:path}" , status_code=status.HTTP_200_OK , response_model=list[str])
async def get_files_under_directory(owner_id : int , txt : str , db : AsyncSession = Depends(get_db)):
    
          
     result = await db.execute(select(Bucket).where(Bucket.owner_id == owner_id))
 
     bucket = result.scalar_one_or_none()

     if not bucket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")
     
     bucket_id = bucket.id

     query = await db.execute(select(Object).where(Object.bucket_id == bucket_id , Object.key.ilike(f"%{txt}%")))

     res = query.scalars().all()

     if not res:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket is empty")
     ls = []
     for i in res:

       file_path = os.path.join("/home/devansh/" , f"{i.key}")
       if not os.path.exists(file_path):
              raise HTTPException(status_code=404, detail=f"{i.key} not found on disk")
       with open(file_path, "r", encoding="utf-8") as file:
          content = file.read()
          ls.append(content)

     return ls     


@router.delete("/{owner_id}/{txt:path}" , status_code=status.HTTP_200_OK , response_model=str)
async def delete_items_in_bucket(owner_id : int , txt : str , db : AsyncSession = Depends(get_db)):

     result = await db.execute(select(Bucket).where(Bucket.owner_id == owner_id))
 
     bucket = result.scalar_one_or_none()

     if not bucket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")
     
     bucket_id = bucket.id

     query = await db.execute(select(Object).where(Object.bucket_id == bucket_id , Object.key == txt))
   
     res = query.scalar_one_or_none()

     if not res:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="File does not exist")
     
     await db.delete(res)

     return f"{res.key} is removed from bucket" 
     