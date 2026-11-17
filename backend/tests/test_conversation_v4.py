"""V4 follows the assistant's own question; no hosted API or Chroma needed."""
from types import SimpleNamespace
from app.services.context_resolver import resolve_context, last_assistant_offer


def message(role, content):
    return SimpleNamespace(role=role, content=content)


def test_yes_to_bp_offer_is_instant_and_correct():
    history = [
        message('user', 'what is bp'),
        message('assistant', 'BP means blood pressure. Would you like a simple explanation of high blood pressure?'),
    ]
    resolved = resolve_context('yes', history, medical_bot=True)
    assert resolved.action == 'approved_followup'
    assert resolved.answer and 'hypertension' in resolved.answer
    assert 'Yes' not in resolved.question


def test_roman_urdu_yes():
    history = [message('assistant', 'Would you like a simple explanation of high blood pressure?')]
    assert resolve_context('haan', history, medical_bot=True).action == 'approved_followup'


def test_no_declines_without_search():
    history = [message('assistant', 'Would you like a simple explanation of high blood pressure?')]
    assert resolve_context('no thanks', history, medical_bot=True).action == 'declined'


def test_yes_without_offer_asks_clarification():
    history = [message('assistant', 'BP is blood pressure.')]
    result = resolve_context('yes', history, medical_bot=True)
    assert result.action == 'clarify'
    assert result.answer is not None


def test_only_last_assistant_turn_may_be_accepted():
    history = [message('assistant','Would you like a simple explanation of high blood pressure?'),
               message('user','actually tell me the price')]
    resolved = resolve_context('yes', history, medical_bot=True)
    assert resolved.action == 'clarify'


def test_unknown_offer_preserves_subtopic_not_word_yes():
    history = [message('assistant','Would you like to compare the two models?')]
    resolved = resolve_context('yes',history)
    assert resolved.action == 'accepted_offer'
    assert 'compare' in resolved.question.lower()


def test_urdu_transform_keeps_context():
    history = [message('assistant','BP means blood pressure.')]
    resolved=resolve_context('explain in urdu', history)
    assert resolved.action=='translation'
    assert 'Urdu' in resolved.question


def test_no_false_offer_if_unrelated_question():
    assert last_assistant_offer('Your BP is 120/80. Do you have any symptoms?') is None


def test_yes_to_two_numbers_has_correct_faq():
    history=[message('assistant','Would you like me to explain what the two numbers mean?')]
    answer=resolve_context('yes', history, medical_bot=True).answer
    assert answer and 'systolic' in answer.lower() and 'diastolic' in answer.lower()


def test_integrated_chat_yes_skips_retrieval_and_llm(monkeypatch):
    """Exercise real Stage 3 service + SQL persistence without Gemini/Chroma."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.db.base import Base
    from app.db.models import User, Company, KB, Bot, Message
    from app.db import ai_models
    from app.schemas.inputs import ChatIn
    import pytest
    pytest.importorskip("pwdlib")  # Installed in normal backend requirements; may be absent in isolated QA.
    from app.services import chat_service

    engine=create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    def should_not_run(*args, **kwargs):
        raise AssertionError('Follow-up must not call retrieval or hosted LLM')
    monkeypatch.setattr(chat_service,'retrieve',should_not_run)
    monkeypatch.setattr(chat_service,'generate',should_not_run)
    with Session(engine) as db:
        user=User(name='Test user',email='test@example.org',password_hash='not-for-auth')
        db.add(user);db.flush()
        c=Company(owner_id=user.id,name='Demo Hospital',industry='Healthcare')
        db.add(c);db.flush()
        kb=KB(company_id=c.id,name='Medical Knowledge')
        db.add(kb);db.flush()
        b=Bot(company_id=c.id,kb_id=kb.id,name='Medical Guideline Assistant')
        db.add(b);db.flush()
        db.add(ai_models.BotPolicy(company_id=c.id,bot_id=b.id,role='medical_education'))
        db.commit()
        first=chat_service.generate_chat_reply(ChatIn(company_id=c.id,knowledgebase_id=kb.id,bot_id=b.id,question='what is bp'),user,db)
        assert 'blood pressure' in first['answer'].lower()
        second=chat_service.generate_chat_reply(ChatIn(company_id=c.id,knowledgebase_id=kb.id,bot_id=b.id,conversation_id=first['conversation_id'],question='yes'),user,db)
        assert second['route']=='approved_followup'
        assert second['usage']['total_tokens'] is None
        assert second['timings']['retrieval_ms']==0
        assert 'hypertension' in second['answer'].lower()
        saved=db.scalars(select(Message).where(Message.conversation_id==first['conversation_id'])).all()
        assert [m.role for m in saved]==['user','assistant','user','assistant']
