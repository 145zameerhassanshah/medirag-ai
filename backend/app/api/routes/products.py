"""Structured catalogue and Chroma indexing."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
from app.rag.store import add_texts, collection

router = APIRouter()

@router.get('/api/companies/{company_id}/products')
def list_products(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return [out(p,['id','kb_id','name','sku','category','description','price','currency','availability']) for p in db.scalars(select(Product).where(Product.company_id==company_id))]

@router.post('/api/companies/{company_id}/products',status_code=201)
def add_product(company_id:str,body:ProductIn,user:UserDep,db:DB):
    owned_company(db,user,company_id);owned_kb(db,company_id,body.kb_id)
    p=Product(company_id=company_id,**body.model_dump());db.add(p);db.flush()
    text=f'Product: {p.name}. SKU: {p.sku}. Category: {p.category}. Description: {p.description}. Price: {p.price} {p.currency}. Availability: {p.availability}.'
    try:add_texts(company_id,p.kb_id,p.id,f'Catalog: {p.name}',[(0,'Product catalogue',text)])
    except Exception:
        db.rollback();raise HTTPException(503,'Product indexing failed')
    db.commit();db.refresh(p)
    return out(p,['id','kb_id','name','sku','category','description','price','currency','availability'])
@router.patch('/api/companies/{company_id}/products/{product_id}')
def edit_product(company_id:str,product_id:str,body:ProductIn,user:UserDep,db:DB):
    owned_company(db,user,company_id);owned_kb(db,company_id,body.kb_id)
    p=db.get(Product,product_id)
    if not p or p.company_id!=company_id:raise HTTPException(404,'Product not found')
    old_kb=p.kb_id
    for field,value in body.model_dump().items():setattr(p,field,value)
    text=f'Product: {p.name}. SKU: {p.sku}. Category: {p.category}. Description: {p.description}. Price: {p.price} {p.currency}. Availability: {p.availability}.'
    try:
        collection(company_id,old_kb).delete(where={'document_id':p.id})
        add_texts(company_id,p.kb_id,p.id,f'Catalog: {p.name}',[(0,'Product catalogue',text)])
    except Exception:
        db.rollback();raise HTTPException(503,'Product re-indexing failed; reconcile index before retry')
    db.commit();return out(p,['id','kb_id','name','sku','category','description','price','currency','availability'])

@router.delete('/api/companies/{company_id}/products/{product_id}')
def delete_product(company_id:str,product_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    p=db.get(Product,product_id)
    if not p or p.company_id!=company_id:raise HTTPException(404,'Product not found')
    collection(company_id,p.kb_id).delete(where={'document_id':p.id})
    db.delete(p);db.commit();return {'deleted':True}
