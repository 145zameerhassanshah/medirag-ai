"""Minimal alpha HTTP tests; requires environment and dependencies; run pytest tests_smoke.py."""
from fastapi.testclient import TestClient
from main import app


def test_health():
    client=TestClient(app)
    r=client.get('/health')
    assert r.status_code==200
    assert r.json()['status']=='ok'


def test_requires_auth():
    client=TestClient(app)
    assert client.get('/api/companies').status_code==401
    assert client.post('/api/chat',json={'company_id':'x','knowledgebase_id':'x','bot_id':'x','question':'Hello'}).status_code==401


def test_query_validation():
    client=TestClient(app)
    assert client.post('/api/chat',json={'company_id':'x','knowledgebase_id':'x','bot_id':'x','question':'   '}).status_code==422
