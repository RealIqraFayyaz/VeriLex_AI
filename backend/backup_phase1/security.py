import jwt
from datetime import datetime,timedelta,timezone
from pwdlib import PasswordHash
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database import get_db
from app.models import User,Role
hasher=PasswordHash.recommended()
oauth=OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
def hash_password(value): return hasher.hash(value)
def verify_password(value,hashed): return hasher.verify(value,hashed)
def make_token(uid):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub":str(uid),"exp":exp,"type":"access"},settings.jwt_secret_key,algorithm="HS256")
async def current_user(token:str=Depends(oauth),db:AsyncSession=Depends(get_db)):
    try:
        p=jwt.decode(token,settings.jwt_secret_key,algorithms=["HS256"])
        if p.get("type")!="access": raise ValueError()
        uid=int(p["sub"])
    except Exception: raise HTTPException(401,"Invalid or expired access token")
    user=await db.scalar(select(User).where(User.id==uid,User.is_active.is_(True)))
    if not user: raise HTTPException(401,"Invalid or expired access token")
    return user
def roles(*allowed):
    async def check(user:User=Depends(current_user)):
        if user.role not in allowed: raise HTTPException(403,"Insufficient permissions")
        return user
    return check
