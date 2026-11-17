"""Resolve short conversational follow-ups against the last assistant turn.

No extra hosted-model request and no schema migration. Previous assistant messages
are already persisted in SQL by Stage 3; the resolution is scoped to the
validated company/bot/conversation in chat_service.

This resolver is intentionally conservative: it never treats a prior answer as
proof of company facts, and never invents an assistant offer that wasn't made.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

YES = frozenset({'yes','yeah','yep','sure','ok','okay','please','go ahead','haan','han','ji','jee','bilkul','yes please','sure please'})
NO = frozenset({'no','nope','not now','no thanks','nah','nahi','nahin'})
MORE = frozenset({'tell me more','explain more','more details','more','elaborate','details','please explain','explain it','detail mein batao'})
URDU = frozenset({'in urdu','explain in urdu','urdu mein','urdu mein samjhao','roman urdu','in roman urdu','translate in urdu'})
OFFER = re.compile(r'\b(would you like|do you want|shall i|should i|want me to|can i explain|would it help if i)\b', re.I)

@dataclass(frozen=True)
class ResolvedContext:
    question: str
    action: str = 'normal'
    answer: str | None = None
    has_context: bool = False
    pending_offer: str | None = None


def _normalize(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip().casefold()).rstrip('?.! ')


def last_assistant_offer(content: str) -> str | None:
    """Extract a recent explicit invitation (not arbitrary assistant questions)."""
    if not content:
        return None
    # Offers can follow other paragraphs and include markdown. Limit inspected text.
    candidates = re.findall(r'[^?\n]{0,260}\?', content[-1400:])
    for candidate in reversed(candidates):
        clean = re.sub(r'[*_`\[\]]', '', candidate).strip()
        if OFFER.search(clean):
            return clean[-280:]
    return None


def _approved_medical_explanation(offer: str, *, medical_bot: bool) -> str | None:
    if not medical_bot:
        return None
    norm = _normalize(offer)
    if 'high blood pressure' in norm or 'hypertension' in norm:
        return (
            '**High blood pressure (hypertension)** means blood pressure stays above a healthy range over time. '
            'It often has no obvious symptoms, so measuring BP is important.\n\n'
            'A reading has two numbers: **systolic** (pressure when the heart beats) and '
            '**diastolic** (pressure between beats). A healthcare professional evaluates repeated '
            'measurements and your health circumstances before recommending treatment.\n\n'
            'Would you like me to explain what the two numbers mean?'
        )
    if 'systolic' in norm and 'diastolic' in norm:
        return (
            '**Systolic** is the top BP number—pressure when the heart pumps. '
            '**Diastolic** is the bottom number—pressure when the heart relaxes between beats. '
            'For example, **120/80 mmHg** means 120 systolic and 80 diastolic.'
        )
    if 'two numbers' in norm or 'bp numbers' in norm:
        return (
            'A blood pressure reading has two numbers. **Systolic** (top) measures pressure '
            'when the heart pumps; **diastolic** (bottom) measures pressure between beats. '
            'For example, in **120/80 mmHg**, 120 is systolic and 80 is diastolic.'
        )
    return None


def resolve_context(message: str, prior_messages, *, medical_bot: bool = False) -> ResolvedContext:
    """prior_messages: oldest-first rows with .role and .content.

    Handles "yes" to an explicit offer, "no", "tell me more", and translation.
    For unknown offers, return a resolved meaningful question so retrieval/model
    never search for a meaningless single-word "yes".
    """
    question = message.strip()
    norm = _normalize(question)
    prior = [m for m in prior_messages if getattr(m, 'role', None) in ('user','assistant')]
    previous = prior[-1] if prior else None
    if previous is None or previous.role != 'assistant':
        if norm in YES | NO:
            return ResolvedContext(question, 'clarify', 'Could you tell me what you would like me to explain or help with?')
        return ResolvedContext(question)

    previous_text = previous.content or ''
    offer = last_assistant_offer(previous_text)
    if norm in NO:
        if offer:
            return ResolvedContext(question, 'declined', 'No problem! What would you like help with next?', True)
        return ResolvedContext(question, 'clarify', 'Sure—what would you like to explore next?')

    if norm in YES:
        if not offer:
            return ResolvedContext(question, 'clarify', 'Sure! What would you like me to explain?', True)
        approved = _approved_medical_explanation(offer, medical_bot=medical_bot)
        if approved:
            return ResolvedContext(offer, 'approved_followup', approved, True, offer)
        # Convert accepted offer into a meaningful standalone retrieval question.
        # General LLM mode is permitted only by explicit bot policy upstream.
        return ResolvedContext(
            'Please fulfill this specific offered follow-up, using only authorized evidence '
            f'where required: {offer}', 'accepted_offer', None, True, offer
        )

    if norm in MORE:
        if offer:
            approved = _approved_medical_explanation(offer, medical_bot=medical_bot)
            if approved:
                return ResolvedContext(offer, 'approved_followup', approved, True, offer)
            return ResolvedContext('Explain in more detail: ' + offer, 'more_details', None, True, offer)
        if previous_text:
            return ResolvedContext(
                'Give a clearer, more detailed explanation of the preceding assistant answer '
                'to the same user question. Avoid adding unsupported facts.',
                'more_details', None, True,
            )

    if norm in URDU:
        # Preserve original answer as text to transform, not as factual evidence.
        # The prompt builder receives the actual previous message via history.
        language = 'Roman Urdu' if 'roman' in norm else 'Urdu'
        return ResolvedContext(
            f'Re-explain the last assistant response in {language}, preserving its meaning '
            'without inventing new company or medical facts.',
            'translation', None, True,
        )

    return ResolvedContext(question)
