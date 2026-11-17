"""Structural guardrail; no secrets or real API calls needed."""
from pathlib import Path
import ast
root = Path(__file__).resolve().parents[1]

def test_all_modules_parse():
    for path in [root / 'main.py', *(root / 'app').rglob('*.py')]:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

def test_route_modules_exist():
    for filename in ('auth.py','organizations.py','knowledgebases.py','bots.py','documents.py','products.py','chat.py','conversations.py'):
        assert (root/'app'/'api'/'routes'/filename).is_file()
