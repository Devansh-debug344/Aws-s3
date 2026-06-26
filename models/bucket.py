from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base


class Bucket(Base):
    __tablename__ = "buckets"

    id = Column(Integer , primary_key = True , index = True)
    owner_id = Column(Integer , ForeignKey("users.id") , nullable = False , unique = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    objects = relationship("Object", back_populates="bucket")

class Object(Base):
    __tablename__ = "objects"

    id         = Column(Integer, primary_key=True)
    key        = Column(String, nullable=False)   # filename / path
    bucket_id  = Column(Integer, ForeignKey("buckets.id"))
    size       = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())   

    bucket = relationship("Bucket" , back_populates = "objects")