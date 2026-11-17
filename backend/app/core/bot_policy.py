"""Central, server-controlled policy. Company-custom content is lower trust."""
from pydantic import BaseModel, Field
from sqlalchemy import select
from app.db.ai_models import BotPolicy

class PolicyInput(BaseModel):
    role: str = Field(default='knowledge', pattern=r'^(knowledge|medical_education|sales|support|content)$')
    language: str = Field(default='auto', pattern=r'^(auto|english|urdu|roman_urdu)$')
    tone: str = Field(default='friendly', pattern=r'^(friendly|professional|concise)$')
    answer_length: str = Field(default='adaptive', pattern=r'^(adaptive|short|detailed)$')
    allow_general: bool = False
    require_citations: bool = True
    max_output_tokens: int = Field(default=420, ge=120, le=1000)
    prompt_version: str = Field(default='p3', pattern=r'^(p1|p2|p3|p4)$')
    company_instructions: str = Field(default='', max_length=1400)

def load_policy(db, company_id: str, bot_id: str) -> PolicyInput:
    record = db.scalar(select(BotPolicy).where(BotPolicy.company_id == company_id, BotPolicy.bot_id == bot_id))
    if record is None:
        return PolicyInput()
    return PolicyInput(role=record.role, language=record.language, tone=record.tone,
                       answer_length=record.answer_length, allow_general=bool(record.allow_general),
                       require_citations=bool(record.require_citations), max_output_tokens=record.max_output_tokens,
                       prompt_version=record.prompt_version, company_instructions=record.company_instructions)

def update_policy(db, company_id: str, bot_id: str, value: PolicyInput) -> PolicyInput:
    record = db.scalar(select(BotPolicy).where(BotPolicy.company_id == company_id, BotPolicy.bot_id == bot_id))
    if record is None:
        record = BotPolicy(company_id=company_id, bot_id=bot_id)
        db.add(record)
    for key, content in value.model_dump().items():
        setattr(record, key, int(content) if isinstance(content, bool) else content)
    db.commit()
    return value
