from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Verify Clerk token and return user_id"""
    
    token = credentials.credentials
    public_key = os.getenv("CLERK_PUBLIC_KEY")
    
    try:
        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="your-clerk-app-id"  # From Clerk dashboard
        )
        
        user_id = payload.get("sub")  # Clerk uses "sub" for user ID
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return user_id
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )