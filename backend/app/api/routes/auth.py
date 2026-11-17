"""User registration, login, profile API."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
from app.core.security import passwords, token

router = APIRouter()

@router.post('/api/auth/register',status_code=201)
def register(body:Register,db:DB):
    email=body.email.strip().lower()
    if db.scalar(select(User).where(User.email==email)):raise HTTPException(409,'Email already registered')
    u=User(name=body.name,email=email,password_hash=passwords.hash(body.password))
    db.add(u);db.commit();db.refresh(u)
    return {'access_token':token(u),'token_type':'bearer','user':out(u,['id','name','email'])}
@router.post('/api/auth/login')
def login(body:Login,db:DB):
    u=db.scalar(select(User).where(User.email==body.email.strip().lower()))
    if not u or not passwords.verify(body.password,u.password_hash):raise HTTPException(401,'Invalid credentials')
    return {'access_token':token(u),'token_type':'bearer','user':out(u,['id','name','email'])}
@router.get('/api/me')
def me(user:UserDep): return out(user,['id','name','email'])
@router.patch('/api/me')
def update_me(body:UserProfileIn,user:UserDep,db:DB):
    current=db.get(User,user.id);current.name=body.name.strip();db.commit()
    return out(current,['id','name','email'])
