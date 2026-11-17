"""Thin chat HTTP controller. Business logic resides in services/chat_service.py."""
from fastapi import APIRouter, Response
from app.db.session import DB
from app.core.security import UserDep
from app.schemas.inputs import ChatIn
from app.services.chat_service import generate_chat_reply

router = APIRouter()

@router.post('/api/chat')
def chat(body: ChatIn, user: UserDep, db: DB, response: Response):
    data=generate_chat_reply(body, user, db)
    times=data.get('timings', {})
    # Visible in Chrome DevTools > Network > Response Headers, in milliseconds.
    fields=[('auth','auth_ms'),('history','history_ms'),('intent','intent_ms'),
            ('catalogue','catalogue_ms'),('retrieval','retrieval_ms'),
            ('generation','generation_ms'),('persist','persistence_ms'),('total','total_ms')]
    response.headers['Server-Timing']=', '.join(
        f'{name};dur={max(0, float(times.get(key, 0))):.0f}'
        for name,key in fields
    )
    response.headers['X-MediRAG-Route']=str(data.get('route','unknown'))
    return data
