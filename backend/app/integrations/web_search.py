"""Tavily integration, disabled without explicit opt-in and server configuration."""
import json, logging, os
from urllib.request import Request, urlopen
from fastapi import HTTPException
logger=logging.getLogger('medirag')

def web_evidence(query: str) -> list[dict]:
    """Explicit Tavily web mode, disabled by default; never treat web as WHO guideline."""
    if os.getenv('WEB_SEARCH_ENABLED', 'false').lower() != 'true':
        raise HTTPException(503, 'Web search is disabled. Enable WEB_SEARCH_ENABLED on the backend.')
    key = os.getenv('TAVILY_API_KEY', '')
    if not key:
        raise HTTPException(503, 'Web search is not configured. Add TAVILY_API_KEY to backend/.env.')
    payload = json.dumps({"query": query[:350], "max_results": 4,
                          "search_depth": "basic", "include_answer": False,
                          "include_raw_content": False, "include_images": False}).encode()
    req = Request('https://api.tavily.com/search', data=payload, method='POST', headers={
        'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=15) as res:
            data = json.load(res)
    except Exception:
        logger.exception('Web search provider failed')
        raise HTTPException(503, 'Web search temporarily unavailable; your documents were not modified.')
    rows = []
    for item in data.get('results', [])[:4]:
        url = item.get('url', '')
        if not url.startswith(('http://', 'https://')):
            continue
        rows.append({'title': str(item.get('title', 'Web page'))[:160], 'url': url,
                     'content': str(item.get('content', ''))[:1200]})
    return rows
