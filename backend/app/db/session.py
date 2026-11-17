"""Single SQLAlchemy engine and database dependency."""
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import DATABASE_URL
ENGINE = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=ENGINE)

def db_session():
    with SessionLocal() as db:
        yield db

DB = Annotated[Session, Depends(db_session)]
