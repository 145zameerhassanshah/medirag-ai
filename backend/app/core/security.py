"""Authentication and current owner-only authorization.

Future multi-member RBAC should replace owned_company with membership policies.
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from app.core.config import JWT_SECRET
from app.db.session import db_session
from app.db.models import User, Company, KB

passwords = PasswordHash.recommended()
def auth(authorization: Annotated[str|None,Header()]=None, db:Session=Depends(db_session)) -> User:
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Sign in required')
    try:
        data=jwt.decode(authorization[7:],JWT_SECRET,algorithms=['HS256'])
        uid=data.get('sub')
        user=db.get(User,uid)
        if not user: raise ValueError('unknown user')
        return user
    except (jwt.PyJWTError,ValueError): raise HTTPException(401,'Invalid or expired token')
UserDep=Annotated[User,Depends(auth)]
def owned_company(db:Session,user:User,company_id:str)->Company:
    c=db.get(Company,company_id)
    if not c or c.owner_id!=user.id: raise HTTPException(404,'Company not found')
    return c
def owned_kb(db:Session, company_id:str,kb_id:str)->KB:
    kb=db.get(KB,kb_id)
    if not kb or kb.company_id!=company_id: raise HTTPException(404,'Knowledgebase not found')
    return kb

def out(obj,fields): return {k:getattr(obj,k) for k in fields}

def token(user):
    return jwt.encode({'sub':user.id,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},JWT_SECRET,algorithm='HS256')
