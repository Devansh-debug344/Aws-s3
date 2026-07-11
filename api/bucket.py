import os
from dotenv import load_dotenv

from auth.verify_token import verify_token
load_dotenv()  
from botocore.exceptions import ClientError
import boto3
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status , UploadFile , Form , File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from Schemas.schemas import BucketItem , BucketItemOut , Object_Out
from db.database import get_db
from models.bucket import Bucket , Object
from sqlalchemy import select

from repositories.bucket_repo import BucketRepo , ObjectRepo
from tasks import process_upload 

 # Load environment variables from .env file

router = APIRouter(prefix="/buckets", tags=["Bucket"])


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


#create a bucket
@router.post("/create_bucket" , response_model = str , status_code=status.HTTP_201_CREATED)
async def create_bucket(payload : BucketItem , user_id = Depends(verify_token) ,  db : AsyncSession = Depends(get_db)):
     bucket = BucketRepo(db)
     get_bucket = await bucket.get_bucket_by_bucket_name(payload.bucket_name)

     if get_bucket:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket already existed")
     
     new_bucket = await bucket.create_bucket(owner_id = user_id , name = payload.bucket_name)
      
     return f"Bucket created successfully with name {new_bucket.name} and owner_id {new_bucket.owner_id}"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)


@router.post("/{bucket_name}", response_model=str, status_code=status.HTTP_201_CREATED)
async def add_item_bucket(
    bucket_name: str,
    object_name: str = Form(),
    file: UploadFile = File(), 
    user_id = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    bucket = BucketRepo(db)
    get_bucket = await bucket.get_bucket_by_bucket_name(bucket_name)

    if get_bucket and get_bucket.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add items to this bucket")

    if not get_bucket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bucket doesn't exist")

    obj = ObjectRepo(db)

    # Read file once, store it
    file_content = await file.read()
    file_size = len(file_content)

    #create bucket
    try:
        s3_client.create_bucket(Bucket=get_bucket.name)
    except ClientError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating bucket try unique name : {e}")
    try:
    # Upload to S3
       s3_client.put_object(
        Bucket=get_bucket.name,
        Key=object_name,
        Body=file_content
       )
    except ClientError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading file: {e}")
    # Save to DB
    new_obj = await obj.add_item_bucket(
        bucket_id=get_bucket.id,
        object_name=object_name,
        size=file_size,
        etag="",
        storage_path=""
    )

    # Queue task
    process_upload.delay(key=object_name, size=file_size)

    return f"Item added successfully to bucket {get_bucket.name} with object name {object_name}"

#get all the elements in bucket               

@router.get("/{bucket_name}/{object_name}" , response_model= dict, status_code=status.HTTP_200_OK)
async def download_bucket_items(bucket_name : str, object_name : str, user_id = Depends(verify_token) , db : AsyncSession = Depends(get_db)):

     bucket_repo = BucketRepo(db)

     bucket = await bucket_repo.get_bucket_by_bucket_name(bucket_name=bucket_name)
 
     
     if not bucket:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Bucket dont exixted")
     
     if bucket.owner_id != user_id:
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN , detail="You dont have permission to access this bucket")

     bucket_id = bucket.id
 
     obj_repo = ObjectRepo(db)

     obj = await obj_repo.get_object_by_bucket_id(bucket_id=bucket_id)
     
     if not obj:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="No object in bucket")
     try:
        response_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn=3600  # URL expires in 1 hour
        )
     except ClientError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating pre-signed URL: {e}")
     
     
     return {
        "object_name": object_name,
        "size": obj[0].size if obj else None,
        "etag": obj[0].etag if obj else None,
        "storage_path": obj[0].storage_path if obj else None,
        "created_at": obj[0].created_at if obj else None,
        "response_url": response_url
        }
       
        