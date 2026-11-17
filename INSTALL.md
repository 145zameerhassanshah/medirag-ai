# MediRAG Performance V5 — Install

## Prerequisites

The current local project must have Stage 3 response engine and V4 conversation intelligence. Stage 2 frontend chat components are optional; the package will place optimized components where Stage 2 expects them.

Stop both servers. Back up your `.env`, SQLite `medirag.db`, and `storage/` privately; back up Git changes. Do **not** upload credentials.

Extract `MediRAG_Performance_V5.zip` into Downloads. Run the installer **from the extracted package** while specifying project root:

```powershell
cd D:\ZAMEER\cmitinternship\Ai_internship\task\medirag_fullstack
python "$HOME\Downloads\MediRAG_Performance_V5\tools\install_v5.py" --project .
python "$HOME\Downloads\MediRAG_Performance_V5\tools\install_v5.py" --project . --apply
```

Or copy **the entire extracted package** into a temporary folder, keeping `tools` and `backend` alongside each other. Do not copy only `install_v5.py`, as it must access source files.

### Backend tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_performance_v5.py -q
python -m pytest tests/test_conversation_v4.py -q
python -m pytest tests/test_response_engine.py -q
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npx tsc --noEmit
npm run dev
```

### Measure the improvement

Open Chrome F12 > Network > Fetch/XHR > POST `/api/chat`. Under Response, inspect `route`, `response_time_ms`, and `timings` (`auth_ms`, `history_ms`, `retrieval_ms`, `generation_ms`, `persistence_ms`). Under Headers, look for `Server-Timing`. **Compare measured before/after runs with similar questions and warm server**.

Manual tests: (a) `what is bp` > `yes` > `yes`, (b) company product price, (c) WHO recommendation with citations, (d) long conversation, (e) error from missing model.

### What this patch does NOT do

- Does not implement true token streaming/SSE. For a slow genuine RAG request, answer still arrives at completion; you should see the measured generation delay.
- Does not guarantee INP below 200ms. React profiler is needed to identify exact slow browser interactions.
- Does not eliminate LLM time for a question that genuinely requires generation.
- No migration of database or vector chunks.

### Rollback

Installer creates a timestamped backup under your home folder `MediRAG-V5-Backup-YYYYMMDD-HHMMSS`. Stop servers and restore `chat_service.py`, `providers.py`, `chat.py`, `page.tsx`, and any pre-existing chat components from that folder. New components and tests can be removed after restoration.

### Security

Diagnostics do not log chat question text, uploaded documents, tokens, or API keys. `Server-Timing` is present only on authenticated chat responses. Company data and authorization remain controlled by existing access checks.
