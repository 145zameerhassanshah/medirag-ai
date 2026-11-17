"""Knowledgebase CRUD."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
from app.rag.store import collection

router = APIRouter()

@router.get('/api/companies/{company_id}/knowledgebases')
def list_kbs(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return [out(k,['id','name','description']) for k in db.scalars(select(KB).where(KB.company_id==company_id))]
@router.post('/api/companies/{company_id}/knowledgebases',status_code=201)
def create_kb(company_id:str,body:KBIn,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    k=KB(company_id=company_id,**body.model_dump());db.add(k);db.commit();db.refresh(k)
    return out(k,['id','name','description'])

@router.patch('/api/companies/{company_id}/knowledgebases/{kb_id}')
def update_kb(company_id: str, kb_id: str, body: KBIn, user: UserDep, db: DB):
    owned_company(db, user, company_id)
    kb = owned_kb(db, company_id, kb_id)
    kb.name = body.name
    kb.description = body.description
    db.commit()
    return out(kb, ['id','name','description'])

@router.delete('/api/companies/{company_id}/knowledgebases/{kb_id}')
def delete_kb(company_id: str, kb_id: str, user: UserDep, db: DB):
    owned_company(db, user, company_id)
    kb = owned_kb(db, company_id, kb_id)
    if (db.scalar(select(Document.id).where(Document.company_id == company_id, Document.kb_id == kb_id))
        or db.scalar(select(Product.id).where(Product.company_id == company_id, Product.kb_id == kb_id))
        or db.scalar(select(Bot.id).where(Bot.company_id == company_id, Bot.kb_id == kb_id))):
        raise HTTPException(409, 'Knowledgebase is not empty; remove its documents, products and bots first')
    # Do not remove vector collection automatically; profile vectors could remain.
    # Block deletion if Chroma still has vectors, preventing inaccessible stale indices.
    if collection(company_id, kb_id).count():
        raise HTTPException(409, 'Knowledgebase still has indexed vectors; clear/sync indexes before deleting')
    db.delete(kb)
    db.commit()
    return {'deleted': True}
