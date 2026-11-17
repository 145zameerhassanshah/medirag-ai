# MediRAG modular backend — safe replacement guide

This is an **architecture-only refactor of the previously delivered V3 `main.py`**. No new tables, RBAC, billing, public widget or token ledger have been implemented. Existing API paths and database/Chroma naming are preserved.

## Before installing

1. Commit or back up current code. On Windows from project root: `git status` then create a feature branch.
2. Stop Uvicorn. Back up `backend/main.py`, `backend/medirag.db`, `backend/storage/`, and `backend/.env` in a secure location.
3. If your local backend differs from the GitHub/V3 code, review the changes first; replacing it could discard new features.

## Copy these files into existing project

- ZIP `backend/app/` -> your `medirag_fullstack/backend/app/`
- ZIP `backend/main.py` -> existing `medirag_fullstack/backend/main.py`
- ZIP `backend/tests/test_structure.py` -> `medirag_fullstack/backend/tests/test_structure.py`
- Do **not** replace `.env`, `requirements.txt`, SQLite DB, Chroma or uploaded PDF files.
- Do **not** copy the `backend/` directory as a nested folder inside the existing backend.

## Test (PowerShell, from backend folder)

```powershell
.\.venv\Scripts\Activate.ps1
python -m compileall -q app main.py
python -m pytest tests/test_structure.py -q
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

In another shell run `python -c "from main import app; print(len(app.routes)); print([r.path for r in app.routes if r.path == '/api/chat'])"` (from backend). Make sure `/health`, `/docs`, existing auth, upload, chat, and conversation history all work. Then test from `http://localhost:3000/live`.

**Important:** The original `main.py` had `Base.metadata.create_all()` and the modular app retains it for compatible local development. For production, create Alembic migrations and remove automatic schema creation after migration validation.

### File ownership
- `core/config.py`: environment settings
- `core/security.py`: JWT auth and owner-only access
- `db/session.py`: SQLAlchemy engine and session
- `db/models.py`: tables
- `schemas/inputs.py`: Pydantic payloads
- `api/routes/`: request endpoints
- `rag/store.py`: embeddings and Chroma
- `rag/ingestion.py`: document parsing
- `rag/providers.py`: Gemini/OpenAI adapter
- `rag/prompts.py`: greetings/fallback helpers
- `integrations/web_search.py`: optional Tavily
- `services/chat_service.py`: existing conversation-aware retrieval, evidence ranking, answer generation, and message persistence
- `app/main.py`: FastAPI app, CORS and router registration

This first stage prioritizes safe modular extraction. Stage 2 should further split `services/chat_service.py` into separately tested retrieval, prompt construction, citation validation, and usage services; add token ledger only through a database migration.
