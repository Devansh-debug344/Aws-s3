from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import User

class UserRepo:

    def __init__(self , session : AsyncSession):
       self.session = session

    async def get_user_by_email(self , email : str ):

        res = await self.session.execute(select(User).where(User.email == email))

        user = res.scalar_one_or_none()

        return user 
    
    async def create_user(self , email : str , username : str , hashed_password : str ) -> User:

     user = User(email = email , username = username , hashed_password = hashed_password)
     self.session.add(user)
     await self.session.flush()
     await self.session.refresh(user)
     return user