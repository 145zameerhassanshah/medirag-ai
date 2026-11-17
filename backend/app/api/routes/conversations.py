"""Saved conversation CRUD."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company, owned_kb, out
from app.db.session import DB
from app.db.models import User, Company, KB, Document, Product, Bot, Conversation, Message
from app.schemas.inputs import Register, Login, UserProfileIn, CompanyIn, KBIn, BotIn, ProductIn, ConversationUpdate, ChatIn
import json

router = APIRouter()

@router.get('/api/companies/{company_id}/conversations')
def conversations(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return [out(c,['id','bot_id','title','created_at']) for c in db.scalars(select(Conversation).where(Conversation.company_id==company_id).order_by(Conversation.created_at.desc()))]
@router.get('/api/companies/{company_id}/conversations/{conversation_id}')
def conversation(company_id:str,conversation_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    conv=db.get(Conversation,conversation_id)
    if not conv or conv.company_id!=company_id:raise HTTPException(404,'Conversation not found')
    messages=db.scalars(select(Message).where(Message.conversation_id==conv.id,Message.company_id==company_id).order_by(Message.created_at)).all()
    return {'id':conv.id,'title':conv.title,'messages':[{'id':m.id,'role':m.role,'content':m.content,'citations':json.loads(m.citations)} for m in messages]}


@router.patch('/api/companies/{company_id}/conversations/{conversation_id}')
def rename_conversation(
    company_id: str,
    conversation_id: str,
    body: ConversationUpdate,
    user: UserDep,
    db: DB,
):
    """Rename an existing conversation within a company owned by this user."""
    owned_company(db, user, company_id)
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.company_id != company_id:
        raise HTTPException(status_code=404, detail='Conversation not found')
    conv.title = body.title
    db.commit()
    db.refresh(conv)
    return {'id': conv.id, 'title': conv.title, 'updated': True}


@router.delete('/api/companies/{company_id}/conversations/{conversation_id}')
def delete_conversation(
    company_id: str,
    conversation_id: str,
    user: UserDep,
    db: DB,
):
    """Delete a conversation and its messages; does not modify documents or ChromaDB."""
    owned_company(db, user, company_id)
    conv = db.get(Conversation, conversation_id)
    if not conv or conv.company_id != company_id:
        raise HTTPException(status_code=404, detail='Conversation not found')

    # Explicitly delete child messages because the existing Message model
    # does not declare ORM relationship cascade behavior.
    messages = db.scalars(
        select(Message).where(
            Message.company_id == company_id,
            Message.conversation_id == conversation_id,
        )
    ).all()
    for message in messages:
        db.delete(message)
    db.delete(conv)
    db.commit()
    return {'deleted': True, 'conversation_id': conversation_id}
