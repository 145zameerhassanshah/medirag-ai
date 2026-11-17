"""Deterministic cheap routing; uncertain company facts always use retrieval."""
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class RouteDecision:
    route: str
    answer: str | None = None

BP_TERMS = {'what is bp', 'what does bp mean', 'what is blood pressure', 'bp kya hai', 'bp kia hai'}
MEDICAL_HINTS = ('health', 'medical', 'hospital', 'clinic', 'medicine', 'medical_education')

def route_question(question: str, *, policy, company, bot) -> RouteDecision:
    q = re.sub(r'\s+', ' ', question.casefold()).strip().rstrip('?!., ')
    greetings = {
        'hello': f'{bot.greeting}', 'hi': f'{bot.greeting}', 'salam': f'{bot.greeting}',
        'thanks': 'You are welcome! Is there anything else I can help with?',
        'thank you': 'You are welcome! Is there anything else I can help with?',
    }
    if q in greetings: return RouteDecision('courtesy', greetings[q])
    if q in BP_TERMS and (policy.role == 'medical_education' or
        any(term in (company.industry + ' ' + bot.name).casefold() for term in MEDICAL_HINTS)):
        return RouteDecision('approved_faq',
          'BP means **blood pressure**: the force of blood against artery walls. '
          'The two numbers are **systolic** (when the heart beats) and **diastolic** '
          '(when it relaxes), for example 120/80 mmHg. '
          'Would you like a simple explanation of high blood pressure?')
    # For company facts, never call general AI as an ungrounded fallback.
    if policy.role == 'content' and any(v in q for v in ('write ', 'caption', 'create ', 'draft ', 'post ', 'marketing')):
        return RouteDecision('content')
    return RouteDecision('rag')

def is_general_question(question: str) -> bool:
    q = question.casefold().strip()
    # Conservative selection: only generic educational definitions/explanations,
    # and avoid industry/brand-specific terms and medical advice requests.
    if any(w in q for w in ('our ', 'your company', 'price', 'cost', 'warranty', 'stock',
                            'refund', 'delivery', 'guideline', 'who recommend',
                            'prescribe', 'my symptoms', 'my medicine', 'dose')):
        return False
    return bool(re.match(r'^(what (is|are|does)|explain|define)\b', q))
