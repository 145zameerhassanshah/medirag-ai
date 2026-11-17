"""Additive Stage 3 tables: existing users, bots and messages stay unchanged."""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, sid, now

class BotPolicy(Base):
    __tablename__ = 'bot_response_policies'
    __table_args__ = (UniqueConstraint('bot_id', name='uq_bot_policy_bot'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=sid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey('companies.id'), index=True)
    bot_id: Mapped[str] = mapped_column(String(36), ForeignKey('bots.id'), index=True)
    role: Mapped[str] = mapped_column(String(32), default='knowledge')
    language: Mapped[str] = mapped_column(String(32), default='auto')
    tone: Mapped[str] = mapped_column(String(32), default='friendly')
    answer_length: Mapped[str] = mapped_column(String(16), default='adaptive')
    allow_general: Mapped[int] = mapped_column(Integer, default=0)
    require_citations: Mapped[int] = mapped_column(Integer, default=1)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=420)
    prompt_version: Mapped[str] = mapped_column(String(16), default='p3')
    company_instructions: Mapped[str] = mapped_column(Text, default='')

class AIUsage(Base):
    __tablename__ = 'ai_usage_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=sid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey('companies.id'), index=True)
    bot_id: Mapped[str] = mapped_column(String(36), index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), index=True)
    route: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(40))
    provider: Mapped[str] = mapped_column(String(40), default='none')
    model: Mapped[str] = mapped_column(String(100), default='none')
    prompt_version: Mapped[str] = mapped_column(String(16), default='p3')
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    retrieval_ms: Mapped[int] = mapped_column(Integer, default=0)
    generation_ms: Mapped[int] = mapped_column(Integer, default=0)
    total_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
