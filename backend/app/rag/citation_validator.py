"""Only accept citation tags actually present in supplied evidence metadata."""
import re

def validate_citations(answer: str, candidates: list[dict], required: bool = True):
    used = set(re.findall(r'\[(S\d+)\]', answer))
    known = {c['source_id'] for c in candidates}
    if used - known:
        return False, []
    if required and not used:
        return False, []
    return bool(answer.strip()), [c for c in candidates if c['source_id'] in used]
