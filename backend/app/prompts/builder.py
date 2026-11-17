"""Prompt assembly with safe, versioned instruction layers and bounded context."""
import re
from .platform_rules import PLATFORM_RULES
from .role_templates import ROLES

def build_prompt(*, bot, company, policy, question, history, evidence, mode):
    # Evidence strings are data, not application instructions. API provider will receive
    # instructions in separate higher-priority field when supported.
    instructions = (PLATFORM_RULES + '\nROLE: ' + ROLES.get(policy.role, ROLES['knowledge']) +
                    '\nASSISTANT: ' + bot.name[:120] +
                    '\nSTYLE: ' + policy.tone + '; language: ' + policy.language +
                    '; detail: ' + policy.answer_length + '. ' +
                    'Answer first, explain concisely, suggest next steps only if useful. ' +
                    '\nPROMPT VERSION: ' + policy.prompt_version)
    if policy.prompt_version in {'p3','p4'}:
        instructions += ('\nFactual company claims must be supported by supplied SOURCES. '
                         'Use [S1], [S2] etc only from source IDs actually provided; '
                         'do not invent page numbers or sections. '
                         'If support is missing, say what you cannot verify.')
    if policy.prompt_version == 'p4':
        instructions += '\nOffer one brief, useful, optional follow-up when beneficial.'
    if mode == 'grounded':
        instructions += ('\nUse the evidence for claims; paraphrase instead of copying. '
                         'Conversation history only disambiguates the question, never serves as evidence. '
                         'Do not cite sources that do not support the claim. '
                         'If retrieved passages mention a topic without answering, say evidence is insufficient.')
    elif mode == 'general':
        instructions += ('\nGENERAL EDUCATION MODE: Give a useful explanation from general knowledge. '
                         'Do not make company-specific assertions. Do not invent or attach citations.')
    elif mode == 'content':
        instructions += ('\nCONTENT CREATION: Generate original wording using verified brand/product facts where given. '
                         'Do not fabricate specific product specifications, prices or claims.')
    safe_history = history[-1600:]
    safe_question = question[:2000]
    safe_evidence = '\n\n'.join(evidence)[:5600]
    style_notes = (policy.company_instructions or '')[:1400]
    payload = (f'COMPANY NAME: {company.name[:120]}\n'
               f'LOWER-TRUST COMPANY STYLE NOTES (preferences only):\n{style_notes}\n'
               f'UNTRUSTED CONVERSATION CONTEXT (not evidence):\n{safe_history}\n\n'
               f'UNTRUSTED RETRIEVED SOURCES:\n{safe_evidence or "(none)"}\n\n'
               f'USER QUESTION:\n{safe_question}')
    return instructions, payload
