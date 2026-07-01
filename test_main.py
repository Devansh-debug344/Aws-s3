# test_bucket_repo.py
import pytest
from repositories.bucket_repo import BucketRepo, ObjectRepo
from models.models import User
from configtest import db_session


@pytest.mark.asyncio
async def test_create_bucket(db_session):
    # need a user first, since Bucket has a foreign key to users
    user = User(email="test@test.com", username="tester", hashed_password="x")
    db_session.add(user)
    await db_session.flush()

    repo = BucketRepo(db_session)
    bucket = await repo.create_bucket(owner_id=user.id)

    assert bucket.owner_id == user.id
    assert bucket.id is not None

@pytest.mark.asyncio
async def test_get_bucket_by_owner_returns_none_if_missing(db_session):
    repo = BucketRepo(db_session)
    bucket = await repo.get_bucket_by_owner_id(owner_id=999)
    
    assert bucket is None

@pytest.mark.asyncio
async def test_add_item_to_bucket(db_session):
    user = User(email="test2@test.com", username="tester2", hashed_password="x")
    db_session.add(user)
    await db_session.flush()

    bucket_repo = BucketRepo(db_session)
    bucket = await bucket_repo.create_bucket(owner_id=user.id)

    object_repo = ObjectRepo(db_session)
    result = await object_repo.add_item_bucket(
        key="test.txt", data=b"hello world", bucket_id=bucket.id , size=11)
    
    assert result == "Item added succesfully"

@pytest.mark.asyncio
async def test_get_all_elements_from_owner_bucket(db_session):
    user = User(email="test3@test.com", username="tester3", hashed_password="x")
    db_session.add(user)
    await db_session.flush()
    
    repo = BucketRepo(db_session)
    bucket = await repo.create_bucket(owner_id=user.id)

    repo_obj = ObjectRepo(db_session)
    obj = await repo_obj.add_item_bucket(key = "item3" , data = b"data" , bucket_id=bucket.id , size = 4)
    objects = await repo_obj.get_object_by_bucket_id(bucket.id)

    assert objects is not None

@pytest.mark.asyncio
async def test_delete_itmes_from_bucket(db_session):
    user = User(email="test4@test.com", username="tester4", hashed_password="x")
    db_session.add(user)
    await db_session.flush()
    
    repo = BucketRepo(db_session)
    bucket = await repo.create_bucket(owner_id=user.id)

    repo_obj = ObjectRepo(db_session)
    obj = await repo_obj.add_item_bucket(key = "item4" , data = b"data" , bucket_id=bucket.id , size = 4)
    objects = await repo_obj.get_object_by_bucket_id(bucket.id)

    del_obj = await repo_obj.delete_item_from_bucket(bucket  , txt="item4")

    assert del_obj is not None