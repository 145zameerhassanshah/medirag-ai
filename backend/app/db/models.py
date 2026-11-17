"""Existing database tables; unchanged columns for migration compatibility."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, sid, now

class User(Base):
    __tablename__='users'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    name: Mapped[str]=mapped_column(String(120))
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Company(Base):
    __tablename__='companies'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    owner_id: Mapped[str]=mapped_column(ForeignKey('users.id'),index=True)
    name: Mapped[str]=mapped_column(String(180))
    industry: Mapped[str]=mapped_column(String(80),default='Other')
    description: Mapped[str]=mapped_column(Text,default='')
    website: Mapped[str]=mapped_column(String(500),default='')
    phone: Mapped[str]=mapped_column(String(100),default='')
    address: Mapped[str]=mapped_column(String(500),default='')
    hours: Mapped[str]=mapped_column(String(250),default='')
    policies: Mapped[str]=mapped_column(Text,default='')
class KB(Base):
    __tablename__='knowledgebases'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(ForeignKey('companies.id'),index=True)
    name: Mapped[str]=mapped_column(String(180))
    description: Mapped[str]=mapped_column(Text,default='')
class Document(Base):
    __tablename__='documents'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(String(36),index=True)
    kb_id: Mapped[str]=mapped_column(String(36),index=True)
    filename: Mapped[str]=mapped_column(String(255))
    storage_path: Mapped[str]=mapped_column(String(700))
    chunks: Mapped[int]=mapped_column(Integer,default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Product(Base):
    __tablename__='products'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(String(36),index=True)
    kb_id: Mapped[str]=mapped_column(String(36),index=True)
    name: Mapped[str]=mapped_column(String(180))
    sku: Mapped[str]=mapped_column(String(100),default='')
    category: Mapped[str]=mapped_column(String(100),default='')
    description: Mapped[str]=mapped_column(Text,default='')
    price: Mapped[str]=mapped_column(String(100),default='')
    currency: Mapped[str]=mapped_column(String(10),default='USD')
    availability: Mapped[str]=mapped_column(String(100),default='Unknown')
class Bot(Base):
    __tablename__='bots'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(String(36),index=True)
    kb_id: Mapped[str]=mapped_column(String(36),index=True)
    name: Mapped[str]=mapped_column(String(120))
    tone: Mapped[str]=mapped_column(String(50),default='Professional')
    greeting: Mapped[str]=mapped_column(String(300),default='How can I help?')
class Conversation(Base):
    __tablename__='conversations'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(String(36),index=True)
    bot_id: Mapped[str]=mapped_column(String(36),index=True)
    title: Mapped[str]=mapped_column(String(200))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
class Message(Base):
    __tablename__='messages'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=sid)
    company_id: Mapped[str]=mapped_column(String(36),index=True)
    conversation_id: Mapped[str]=mapped_column(String(36),index=True)
    role: Mapped[str]=mapped_column(String(20))
    content: Mapped[str]=mapped_column(Text)
    citations: Mapped[str]=mapped_column(Text,default='[]')
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now)
