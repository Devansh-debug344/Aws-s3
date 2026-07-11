import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)

response = s3_client.put_object(
    Bucket='benstokes787097947335',
    Key='test-from-python.txt',
    Body=b'test content from python'
)

print(response)