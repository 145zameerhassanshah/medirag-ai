"""FastAPI entrypoint: route wiring and schema creation for legacy local development.

No schema changes are performed by this modular extraction. Replace create_all
with Alembic migrations in a later dedicated database stage.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import config  # ensures .env loaded before database initialization
from app.db.base import Base
from app.db.session import ENGINE
from app.db import models  # registers existing SQLAlchemy models
from app.db import ai_models  # registers additive policy/usage tables
from app.api.routes import auth, organizations, knowledgebases, bots, documents, products, chat, conversations, assistant_settings

Base.metadata.create_all(ENGINE)
app = FastAPI(title='MediRAG Alpha API', version='0.3.0')
app.add_middleware(CORSMiddleware,
    allow_origins=[s.strip() for s in os.getenv('CORS_ORIGINS','http://localhost:3000').split(',')],
    allow_credentials=True, allow_methods=['GET','POST','PATCH','DELETE'],
    allow_headers=['Authorization','Content-Type'])

@app.get('/health')
def health():
    return {'status':'ok','version':'0.1.0','llm_provider':os.getenv('LLM_PROVIDER','none')}

for router in (auth.router, organizations.router, knowledgebases.router,
               bots.router, documents.router, products.router,
               chat.router, conversations.router, assistant_settings.router):
    app.include_router(router)
