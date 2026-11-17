"""Thin orchestration: security -> intent -> catalogue -> retrieval -> grounded LLM -> validation -> persistence."""
from __future__ import annotations
import json
import logging
import os
import re
import time
from sqlalchemy import select
from fastapi import HTTPException
from app.core.security import owned_company, owned_kb
from app.core.bot_policy import load_policy
from app.db.models import Bot, Conversation, Message
from app.rag.retrieval import retrieve
from app.rag.providers import generate
from app.rag.citation_validator import validate_citations
from app.prompts.builder import build_prompt
from app.services.catalogue_lookup import lookup_product_answer
from app.services.intent_router import route_question, is_general_question
from app.services.usage_service import record_usage
from app.services.context_resolver import resolve_context
from app.integrations.web_search import web_evidence

logger=logging.getLogger('medirag')
FALLBACK = "I couldn't verify that from the company's available information. Would you like to try a more specific question or contact the company?"

def _ms(start):
    return round((time.perf_counter() - start) * 1000)

def generate_chat_reply(body, user, db):
    start=time.perf_counter()
    company=owned_company(db,user,body.company_id)
    owned_kb(db,company.id,body.knowledgebase_id)
    bot=db.get(Bot,body.bot_id)
    if not bot or bot.company_id != company.id or bot.kb_id != body.knowledgebase_id:
        raise HTTPException(404,'Bot not found in this knowledgebase')
    policy=load_policy(db,company.id,bot.id)
    if body.conversation_id:
        conv=db.get(Conversation,body.conversation_id)
        if not conv or conv.company_id != company.id or conv.bot_id != bot.id:
            raise HTTPException(404,'Conversation not found')
    else:
        conv=Conversation(company_id=company.id,bot_id=bot.id,title=body.question[:100]); db.add(conv);db.flush()

    authorization_ms=_ms(start)
    t_history=time.perf_counter()
    # Only the latest messages are needed for V4 context resolution. Loading every
    # message in a long-lived conversation makes each new turn progressively slower.
    latest=db.scalars(select(Message).where(
        Message.company_id==company.id, Message.conversation_id==conv.id,
        Message.role.in_(('user','assistant'))
    ).order_by(Message.created_at.desc(), Message.id.desc()).limit(8)).all()
    usable=list(reversed(latest))[-6:]
    history='\n'.join(f'{m.role}: {m.content[:420]}' for m in usable[-4:])
    medical_bot=(policy.role == 'medical_education' or
                 any(k in (company.industry+' '+bot.name).casefold()
                     for k in ('medical','hospital','health','clinic')))
    history_ms=_ms(t_history)
    t_intent=time.perf_counter()
    resolution=resolve_context(body.question,usable,medical_bot=medical_bot)
    effective_question=resolution.question
    last_user=next((m.content for m in reversed(usable) if m.role=='user'),'')
    followup=bool(not resolution.has_context and last_user and (
        len(body.question.split())<=7 or
        re.search(r'\b(it|they|them|those|their|what about|and for|also)\b',body.question,re.I)))
    context_query=(last_user[:200]+' '+effective_question) if followup else None

    answer=FALLBACK; status='insufficient_context';citations=[]
    route='rag'; provider='none'; model='none'; input_tokens=output_tokens=total_tokens=None
    retrieval_ms=0; generation_ms=0

    decision=route_question(effective_question,policy=policy,company=company,bot=bot)
    intent_ms=_ms(t_intent)
    catalogue_ms=0
    try:
        if resolution.answer is not None:
            answer=resolution.answer
            route='approved_followup' if resolution.action=='approved_followup' else 'conversation'
            status='answered'
        elif decision.answer is not None:
            answer=decision.answer
            route=decision.route
            status='answered'
        else:
            if (policy.allow_general and (is_general_question(effective_question) or resolution.action in ('accepted_offer','more_details','translation')) and not body.web_search
                and decision.route != 'content' and company.name.casefold() not in effective_question.casefold()):
                # Explicit opt-in: general knowledge does not require document search.
                candidate_citations=[];evidence=[];route='general'
            elif body.web_search:
                # Explicit opt-in; external search results are not company-certified evidence.
                t=time.perf_counter(); pages=web_evidence(context_query or effective_question)
                retrieval_ms=_ms(t)
                candidate_citations=[];evidence=[]
                for item in pages[:4]:
                    sid=f'S{len(candidate_citations)+1}'
                    candidate_citations.append({'source_id':sid,'document_id':None,'filename':item['title'],
                        'page_start':None,'section':'Web search','score':None,'excerpt':item['content'][:240],
                        'url':item['url'],'type':'web'})
                    evidence.append(f'[{sid}] WEB SOURCE: {item["title"]} | {item["url"]}\n{item["content"][:1200]}')
                route='web'
            else:
                # Verified structured product lookup for unambiguous basic facts.
                t_catalogue=time.perf_counter()
                direct=lookup_product_answer(db,company_id=company.id,kb_id=body.knowledgebase_id,question=effective_question)
                catalogue_ms=_ms(t_catalogue)
                if direct is not None:
                    answer=direct;route='catalogue';status='answered'
                candidate_citations=[];evidence=[]
                if direct is None and decision.route != 'content':
                    t=time.perf_counter()
                    candidate_citations,evidence=retrieve(company_id=company.id,kb_id=body.knowledgebase_id,
                        question=effective_question,followup_query=context_query,top_k=body.top_k,threshold=body.threshold)
                    retrieval_ms=_ms(t)

            if status != 'answered':
                mode='grounded' if evidence else None
                if decision.route == 'content':
                    # Content mode: try company evidence before generation.
                    if not body.web_search:
                        t=time.perf_counter()
                        candidate_citations,evidence=retrieve(company_id=company.id,kb_id=body.knowledgebase_id,
                            question=effective_question,followup_query=context_query,top_k=body.top_k,threshold=body.threshold)
                        retrieval_ms=_ms(t)
                    mode='content'  # Creative wording allowed; unverified company facts never allowed
                    route='content'
                elif evidence:
                    route='web' if body.web_search else 'rag'
                if mode is None and policy.allow_general and (is_general_question(effective_question) or resolution.action in ('accepted_offer','more_details','translation')) and not body.web_search:
                    mode='general';route='general'
                if mode:
                    instructions,input_text=build_prompt(bot=bot,company=company,policy=policy,
                        question=effective_question,history=history,evidence=evidence,mode=mode)
                    provider=os.getenv('LLM_PROVIDER','none').strip().lower()
                    model=os.getenv('GEMINI_MODEL' if provider=='gemini' else 'OPENAI_MODEL','none')
                    t=time.perf_counter()
                    result=generate(instructions=instructions,input_text=input_text,
                                    max_output_tokens=policy.max_output_tokens)
                    generation_ms=_ms(t)
                    provider=result.provider;model=result.model
                    input_tokens=result.input_tokens;output_tokens=result.output_tokens;total_tokens=result.total_tokens
                    candidate_answer=result.text.strip()
                    if mode in ('grounded','content'):
                        # Content outputs may be creative; factual source claims still must be grounded.
                        required = bool(policy.require_citations and mode=='grounded')
                        valid,used=validate_citations(candidate_answer,candidate_citations,required=required)
                        if valid:
                            answer=candidate_answer;citations=used;status='answered'
                        else:
                            answer="I couldn't verify a properly cited answer from the available sources. Please ask a more specific question."
                            status='citation_validation_failed'
                    else:
                        if candidate_answer:
                            # General answers must not masquerade as sourced company claims.
                            answer=candidate_answer;status='answered';citations=[]
                elif body.web_search:
                    answer='I could not find suitable web results to answer that reliably.'
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        logger.exception('MediRAG chat failed at route %s (%s)',route,type(exc).__name__)
        answer='The assistant could not complete the request. Please try again.'
        status='llm_unavailable' if route in ('rag','web','general','content') else 'error'
        citations=[]

    t_persist=time.perf_counter()
    measured_before_persistence=_ms(start)
    db.add(Message(company_id=company.id,conversation_id=conv.id,role='user',content=body.question))
    if status not in ('llm_unavailable','error'):
        db.add(Message(company_id=company.id,conversation_id=conv.id,role='assistant',
                       content=answer,citations=json.dumps(citations)))
    record_usage(db,company_id=company.id,bot_id=bot.id,conversation_id=conv.id,
                 route=route,status=status,provider=provider,model=model,prompt_version=policy.prompt_version,
                 input_tokens=input_tokens,output_tokens=output_tokens,total_tokens=total_tokens,
                 retrieval_ms=retrieval_ms,generation_ms=generation_ms,total_ms=measured_before_persistence)
    db.commit()
    persistence_ms=_ms(t_persist)
    total_ms=_ms(start)
    # One trace per request, without logging customer questions or source text.
    logger.info('chat route=%s status=%s total_ms=%d auth_ms=%d history_ms=%d intent_ms=%d catalogue_ms=%d retrieval_ms=%d generation_ms=%d persist_ms=%d',
                route,status,total_ms,authorization_ms,history_ms,intent_ms,catalogue_ms,retrieval_ms,generation_ms,persistence_ms)
    return {'answer':answer,'status':status,'citations':citations,'conversation_id':conv.id,
            'response_time_ms':total_ms,
            'timings':{'auth_ms':authorization_ms,'history_ms':history_ms,'intent_ms':intent_ms,
                       'catalogue_ms':catalogue_ms,'retrieval_ms':retrieval_ms,
                       'generation_ms':generation_ms,'persistence_ms':persistence_ms,
                       'total_ms':total_ms},
            'route':route,'usage':{'provider':provider,'model':model,'input_tokens':input_tokens,
                                  'output_tokens':output_tokens,'total_tokens':total_tokens},
            'prompt_version':policy.prompt_version,
            'resolved_intent':resolution.action}
