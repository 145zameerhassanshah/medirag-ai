"""Structured usage records. Null token values mean unavailable, not zero."""
from sqlalchemy import func, select
from app.db.ai_models import AIUsage

def record_usage(db, *, company_id, bot_id, conversation_id, route, status,
                 provider='none', model='none', prompt_version='p3',
                 input_tokens=None, output_tokens=None, total_tokens=None,
                 retrieval_ms=0, generation_ms=0, total_ms=0):
    db.add(AIUsage(company_id=company_id, bot_id=bot_id, conversation_id=conversation_id,
                   route=route, status=status, provider=provider, model=model,
                   prompt_version=prompt_version, input_tokens=input_tokens,
                   output_tokens=output_tokens, total_tokens=total_tokens,
                   retrieval_ms=retrieval_ms, generation_ms=generation_ms, total_ms=total_ms))

def usage_summary(db, company_id):
    rows = db.scalars(select(AIUsage).where(AIUsage.company_id == company_id)).all()
    return {'requests': len(rows), 'llm_calls': sum(1 for r in rows if r.provider != 'none'),
            'known_input_tokens': sum(r.input_tokens or 0 for r in rows),
            'known_output_tokens': sum(r.output_tokens or 0 for r in rows),
            'unknown_token_events': sum(1 for r in rows if r.provider != 'none' and r.total_tokens is None),
            'average_ms': round(sum(r.total_ms for r in rows) / len(rows), 1) if rows else 0,
            'routes': {route: sum(1 for r in rows if r.route == route) for route in sorted({r.route for r in rows})}}
