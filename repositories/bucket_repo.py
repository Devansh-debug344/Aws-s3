from sqlalchemy.ext.asyncio import AsyncSession
from models.bucket import Bucket , Object
from sqlalchemy import select 

class BucketRepo:

    def __init__(self , session : AsyncSession):
       self.session = session

    async def get_bucket_by_owner_id(self , owner_id : int ) -> Bucket | None:

        res = await self.session.execute(select(Bucket).where(owner_id == Bucket.owner_id))

        bucket = res.scalar_one_or_none()

        return bucket
    async def get_bucket_by_bucket_name(self , bucket_name : str ) -> Bucket | None:

        res = await self.session.execute(select(Bucket).where(bucket_name == Bucket.name))

        bucket = res.scalar_one_or_none()

        return bucket
    
    async def create_bucket(self , owner_id : int , name : str ) -> Bucket:

     bucket = Bucket(owner_id = owner_id , name = name)
     self.session.add(bucket)
     await self.session.flush()
     await self.session.refresh(bucket)
     return bucket
    
class ObjectRepo:

    def __init__(self , session : AsyncSession):
       self.session = session

    async def get_object_by_bucket_id(self , bucket_id : int):

        res = await self.session.execute(select(Object).where(Object.bucket_id == bucket_id))

        obj = res.scalars().all()

        return obj

    async def add_item_bucket( self  , bucket_id: int , object_name: str, size: int , etag: str , storage_path : str ) -> str:
        
       obj = Object(bucket_id  = bucket_id , object_name = object_name, size = size, etag = etag, storage_path = storage_path)
       self.session.add(obj)
       await self.session.flush()
       await self.session.refresh(obj)

       return f"Item added succesfully"

    async def delete_item_from_bucket(self , bucket  , txt : str) -> str:
       
       
       obj = await self.session.execute(select(Object).where(Object.bucket_id == bucket.id , Object.key == txt))

       res = obj.scalar_one_or_none()

       if not res: 
          return None

       await self.session.delete(res)
       return f"{res.key} is removed from bucket"  
    