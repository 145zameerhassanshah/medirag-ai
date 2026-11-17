"""Company profile and knowledge sync API."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
from app.rag.store import collection, add_texts

router = APIRouter()

@router.get('/api/companies')
def companies(user:UserDep,db:DB):
    return [out(x,['id','name','industry','description','website','phone','address','hours','policies']) for x in db.scalars(select(Company).where(Company.owner_id==user.id)).all()]
@router.post('/api/companies',status_code=201)
def create_company(body:CompanyIn,user:UserDep,db:DB):
    c=Company(owner_id=user.id,**body.model_dump());db.add(c);db.commit();db.refresh(c)
    return out(c,['id','name','industry','description','website','phone','address','hours','policies'])
@router.patch('/api/companies/{company_id}')
def edit_company(company_id:str,body:CompanyIn,user:UserDep,db:DB):
    c=owned_company(db,user,company_id)
    for k,v in body.model_dump().items():setattr(c,k,v)
    db.commit();return {'updated':True}

@router.post('/api/companies/{company_id}/sync-profile')
def sync_profile(company_id:str,user:UserDep,db:DB,kb_id:str):
    c=owned_company(db,user,company_id);owned_kb(db,company_id,kb_id)
    text='Company: '+c.name+'\nIndustry: '+c.industry+'\nDescription: '+c.description+'\nWebsite: '+c.website+'\nPhone: '+c.phone+'\nAddress: '+c.address+'\nHours: '+c.hours+'\nPolicies: '+c.policies
    docid='company_'+company_id
    col=collection(company_id,kb_id)
    col.delete(where={'document_id':docid})
    return {'chunks_indexed':add_texts(company_id,kb_id,docid,'Company profile',[(0,'Company information',text)])}
