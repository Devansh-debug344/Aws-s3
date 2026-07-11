import datetime
from uuid import uuid4

from sqlalchemy import UUID, UUID, BigInteger, BigInteger, Boolean, Boolean, Column, Integer, String, ForeignKey, DateTime, func , LargeBinary
from sqlalchemy.orm import relationship
from db.database import Base


class Bucket(Base):
    __tablename__ = "buckets"
     #bucket metadata
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(63), unique=True, nullable=False)
    owner_id = Column(Integer, nullable=False)
    versioning_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    objects = relationship("Object", back_populates="bucket")

class Object(Base):
    __tablename__ = "objects"
    #object metadata
    id = Column(UUID, primary_key=True, default=uuid4)
    bucket_id = Column(UUID, ForeignKey("buckets.id"), nullable=False)
    object_name = Column(String, nullable=False)
    size = Column(BigInteger, default=0)
    etag = Column(String(255))
    storage_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    bucket = relationship("Bucket" , back_populates = "objects")