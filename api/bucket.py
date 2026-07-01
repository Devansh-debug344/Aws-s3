from fastapi import APIRouter, Depends, HTTPException, status , UploadFile , Form , File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from Schemas.schemas import BucketItem , BucketItemOut , Object_Out
from db.database import get_db
from models.bucket import Bucket , Object
from sqlalchemy import select
import os
from repositories.bucket_repo import BucketRepo , ObjectRepo
router = APIRouter(prefix="/buckets", tags=["Bucket"])

#create a bucket
@router.post("/create_bucket" , response_model = BucketItemOut , status_code=status.HTTP_201_CREATED)
async def create_bucket(payload : BucketItem , db : AsyncSession = Depends(get_db)):
     bucket = BucketRepo(db)
     get_bucket = await bucket.get_bucket_by_owner_id(payload.owner_id)

     if get_bucket:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket already existed")
     
     new_bucket = await bucket.create_bucket(payload.owner_id)
      
     return new_bucket
#post item in bucket
@router.post("/" , response_model = str , status_code=status.HTTP_201_CREATED)
async def add_item_bucket( owner_id : int = Form() , key : str = Form() , file : UploadFile = File() ,db : AsyncSession = Depends(get_db)):
        
       bucket = BucketRepo(db)

       get_bucket = await bucket.get_bucket_by_owner_id(owner_id)
       if not get_bucket:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont existed")
       obj =  ObjectRepo(db)

       data = await file.read()

       new_obj = await obj.add_item_bucket(key = key , data = data , bucket_id = get_bucket.id ,  size = len(data))
     
       return new_obj

#get all the elements in bucket               

@router.get("/{owner_id}" , response_model=list[Object_Out] , status_code=status.HTTP_200_OK)
# or just remove it, 200 is the default for GET)
async def get_bucket_items(owner_id : int , db : AsyncSession = Depends(get_db)):

     bucket_repo = BucketRepo(db)

     bucket = await bucket_repo.get_bucket_by_owner_id(owner_id=owner_id)
 
     
     if not bucket:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")

     bucket_id = bucket.id
 
     obj_repo = ObjectRepo(db)

     obj = obj_repo.get_object_by_bucket_id(bucket_id=bucket_id)
     
     if not obj:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="No object in bucket")
     
     return obj
         

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

     bucket_repo = BucketRepo(db)

     bucket = await bucket_repo.get_bucket_by_owner_id(owner_id=owner_id)

     if not bucket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont existed")
     
     
     obj_repo = ObjectRepo(db)
     
     res = await obj_repo.delete_item_from_bucket(bucket, txt)
   
     if not res:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="File does not exist")

     return res 

@router.get("/download/{owner_id}/{key:path}")
async def download_file(owner_id: int, key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bucket).where(Bucket.owner_id == owner_id))
    bucket = result.scalar_one_or_none()

    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")

    query = await db.execute(select(Object).where(
        Object.bucket_id == bucket.id,
        Object.key == key
    ))
    obj = query.scalar_one_or_none()

    if not obj:
        raise HTTPException(status_code=404, detail="File not found")

    return Response(
        content=obj.data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={key.split('/')[-1]}"}
    )