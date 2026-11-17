"""Company-owner bot policies and usage metrics; no public write endpoints."""
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.core.security import UserDep, owned_company
from app.db.session import DB
from app.db.models import Bot
from app.core.bot_policy import PolicyInput, load_policy, update_policy
from app.services.usage_service import usage_summary

router=APIRouter(prefix='/api/companies/{company_id}',tags=['Assistant configuration'])

def ensure_bot(db,company_id,bot_id):
    bot=db.get(Bot,bot_id)
    if not bot or bot.company_id != company_id:
        raise HTTPException(404,'Bot not found')
    return bot

@router.get('/bots/{bot_id}/response-policy')
def get_response_policy(company_id: str,bot_id: str,user: UserDep,db: DB):
    owned_company(db,user,company_id)
    ensure_bot(db,company_id,bot_id)
    return load_policy(db,company_id,bot_id)

@router.put('/bots/{bot_id}/response-policy')
def put_response_policy(company_id:str,bot_id:str,body:PolicyInput,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    ensure_bot(db,company_id,bot_id)
    return update_policy(db,company_id,bot_id,body)

@router.get('/usage/summary')
def get_usage_summary(company_id:str,user:UserDep,db:DB):
    owned_company(db,user,company_id)
    return usage_summary(db,company_id)
