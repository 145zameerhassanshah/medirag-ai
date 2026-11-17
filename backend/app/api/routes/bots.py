"""Assistant configuration CRUD."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn

router = APIRouter()

@router.get('/api/companies/{company_id}/bots')
def list_bots(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return [out(b,['id','name','kb_id','tone','greeting']) for b in db.scalars(select(Bot).where(Bot.company_id==company_id))]
@router.post('/api/companies/{company_id}/bots',status_code=201)
def create_bot(company_id:str,body:BotIn,user:UserDep,db:DB):
    owned_company(db,user,company_id);owned_kb(db,company_id,body.kb_id)
    b=Bot(company_id=company_id,**body.model_dump());db.add(b);db.commit();db.refresh(b)
    return out(b,['id','name','kb_id','tone','greeting'])

@router.patch('/api/companies/{company_id}/bots/{bot_id}')
def update_bot(company_id: str, bot_id: str, body: BotIn, user: UserDep, db: DB):
    owned_company(db, user, company_id)
    owned_kb(db, company_id, body.kb_id)
    bot = db.get(Bot, bot_id)
    if not bot or bot.company_id != company_id:
        raise HTTPException(404, 'Bot not found')
    if bot.kb_id != body.kb_id and db.scalar(select(Conversation.id).where(Conversation.bot_id == bot.id)):
        raise HTTPException(409, 'Cannot move a bot with existing conversations to another knowledgebase')
    for key, val in body.model_dump().items():
        setattr(bot, key, val)
    db.commit()
    return out(bot, ['id','name','kb_id','tone','greeting'])

@router.delete('/api/companies/{company_id}/bots/{bot_id}')
def delete_bot(company_id: str, bot_id: str, user: UserDep, db: DB):
    owned_company(db, user, company_id)
    bot = db.get(Bot, bot_id)
    if not bot or bot.company_id != company_id:
        raise HTTPException(404, 'Bot not found')
    if db.scalar(select(Conversation.id).where(Conversation.bot_id == bot.id)):
        raise HTTPException(409, 'Delete its conversations first; bot deletion is blocked to avoid lost history')
    db.delete(bot)
    db.commit()
    return {'deleted': True}
