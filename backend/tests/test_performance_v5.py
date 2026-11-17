"""Stage 5 regression: source structure and HTML independent response timing."""
from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]

def test_chat_service_compiles():
    ast.parse((ROOT/'app/services/chat_service.py').read_text())

def test_v4_context_preserved():
    src=(ROOT/'app/services/chat_service.py').read_text()
    assert 'resolve_context(' in src
    assert 'latest=db.scalars(' in src
    assert '.limit(8)' in src
    assert 'generation_ms' in src and 'persistence_ms' in src

def test_provider_timeouts_and_client_reuse():
    src=(ROOT/'app/rag/providers.py').read_text()
    assert '_gemini_client(' in src
    assert '@lru_cache' in src
    assert 'MEDIRAG_MODEL_TIMEOUT_S' in src

def test_route_server_timing():
    src=(ROOT/'app/api/routes/chat.py').read_text()
    assert 'Server-Timing' in src
    assert 'X-MediRAG-Route' in src
