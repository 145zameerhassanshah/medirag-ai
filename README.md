# MediRAG AI — Real RAG Backend + Next.js Connected Workspace (Alpha)

This is a **runnable development-alpha starter**, not a finished production SaaS. It combines the existing UI-preview app with a new authenticated `/live` workspace and a Python FastAPI backend. It does not modify the old Day 1–4 clinical project.

## Implemented and functional when dependencies/provider keys are configured

- Owner account registration/login (JWT, Argon2 password hashing)
- Multiple owner-scoped company profiles (description, industry, contact, address, hours, policies)
- Company-scoped knowledgebases and chatbot records
- Upload/index digital PDF, DOCX, TXT, Markdown; citation source metadata includes PDF page and heuristic heading (if present)
- Sentence Transformers embeddings and locally persisted ChromaDB cosine search
- Structured product catalogues indexed as searchable text; add and delete
- Company profile sync into a chosen knowledgebase
- Retrieval threshold + unsupported-evidence fallback
- Real LLM generation via configurable Gemini **or** OpenAI server-side API key
- Server-side check that citations reference retrieved IDs (NOT a guarantee of clinical faithfulness)
- Conversation persistence and retrieval in SQL database
- Responsive Next.js `/live` workspace for real CRUD and chat
- Existing UI preview retained on `/dashboard` and other original pages

## Not completed (required before production/client deployment)

**Do not call the alpha production-ready.** Missing: team roles / invites / RBAC, secure HttpOnly session cookies and CSRF protection, email verification, password recovery, rate limiting, upload virus scanning, advanced file validation, audit logs, asynchronous indexing queue, OCR for scanned PDFs, rigorous citation/claim verification, model safety evaluation, source access endpoint / citation click-through, billing, subscription enforcement, customer-facing widget and public-safe API, role-based super admin, background jobs, observability, backups, privacy compliance and infrastructure-hardening. Only the signed-in **company owner** can access its resources; secure shared teams are not yet implemented. Only upload non-sensitive, authorized documents.

## Folder layout

```text
medirag_fullstack/
  backend/
    main.py                # FastAPI routes, SQL models, ingestion, retrieval, generation
    requirements.txt
    .env.example
  frontend/
    src/app/live/page.tsx  # Real API-connected workspace
    src/components/Workbench.tsx # Original demo screens, link to /live
    package.json
    .env.example
```

## Windows install — backend

Open a **new terminal** in `medirag_fullstack/backend`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Python 3.12 is a *recommended* compatibility target for the ML stack; it is okay to use 3.11 if installed. Your existing Python 3.14 virtual environment is not changed. Do not overwrite the Day 1–4 project's `.venv`.

Generate a secret using:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Edit `backend/.env`:

```env
JWT_SECRET=<paste-the-generated-secret>
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your-own-provider-API-key>
GEMINI_MODEL=gemini-2.5-flash
```

Or use `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_MODEL` instead. Choose a model to which your provider account has access. No API keys are supplied or included in this package. API provider charges/free usage depend on the provider and plan. Use `LLM_PROVIDER=none` to test indexing and retrieval setup; grounded answer generation will then return a clear unavailable status.

**Important:** The first embedding run downloads `sentence-transformers/all-MiniLM-L6-v2`. If your C: drive is full, set Hugging Face cache before starting:

```powershell
$env:HF_HOME = "D:\huggingface_cache"
$env:HF_HUB_CACHE = "D:\huggingface_cache\hub"
```

Start:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Verify in browser: http://127.0.0.1:8000/docs and http://127.0.0.1:8000/health

For **local development only**, SQLite is the default database (`backend/medirag.db`) and ChromaDB persists under `backend/storage/chroma`. To use a PostgreSQL server later, configure `DATABASE_URL=postgresql+psycopg://...` and install `psycopg[binary]`, plus proper schema migrations/backups.

## Windows install — frontend

Open **another terminal** inside `medirag_fullstack/frontend`:

```powershell
npm install
Copy-Item .env.example .env.local
```

Make sure `.env.local` contains:

```env
NEXT_PUBLIC_RAG_API_BASE_URL=http://127.0.0.1:8000
```

Start:

```powershell
npm run dev
```

Open:
- http://localhost:3000/live — **REAL connected workspace**, with account sign-in and actual backend operations
- http://localhost:3000/dashboard — earlier **local demo UI** (does not sync with API)

Do not use `/playground` for live testing: the original prototype sends different demo IDs and is not authenticated. Use **`/live` → `Live Chat`** instead. The UI demo's super-admin switch does **not** grant actual super-admin authority.

## End-to-end test flow

1. Register owner account using a testing email and long password.
2. Create a Company profile (e.g., an approved fictional demo business), save policies/hours.
3. Create a knowledgebase.
4. Click **Sync profile** so the company profile is included in search.
5. Add product catalogue entries if testing commerce.
6. Upload a text-based PDF, TXT, Markdown or DOCX; wait for actual index completion.
7. Create a chatbot assigned to that knowledgebase.
8. Go to **Live Chat**, choose the bot and ask a question actually supported by the uploaded data.
9. Verify the response and source excerpt; compare page/heading against the source PDF.
10. Ask an unsupported question and verify fallback. Refresh browser and verify History.
11. Register a second account and ensure it cannot view the first account's company data.

### Verify with curl or API docs

`GET /health` requires no login. All other business data operations require `Authorization: Bearer <access_token>`.

## API routes

| Endpoint | Description |
|---|---|
| POST `/api/auth/register`, `/api/auth/login` | Account and tokens |
| GET `/api/me` | User profile |
| GET/POST `/api/companies` | List/create company |
| PATCH `/api/companies/{company_id}` | Update company profile |
| GET/POST `/api/companies/{company_id}/knowledgebases` | Collections |
| GET/POST `/api/companies/{company_id}/bots` | Chatbot records |
| GET/POST `/api/companies/{company_id}/documents` | Uploaded documents |
| DELETE `/api/companies/{company_id}/documents/{document_id}` | Remove document + vectors |
| GET/POST/PATCH `/api/companies/{company_id}/products` | Catalogue |
| DELETE `/api/companies/{company_id}/products/{product_id}` | Delete catalogue entry + vectors |
| POST `/api/companies/{company_id}/sync-profile?kb_id=...` | Index company profile |
| POST `/api/chat` | Tenant-scoped real RAG |
| GET `/api/companies/{company_id}/conversations` | Conversation list |
| GET `/api/companies/{company_id}/conversations/{conversation_id}` | Conversation messages |

### Example live RAG request

```json
{
  "company_id": "<real-company-uuid>",
  "knowledgebase_id": "<real-kb-uuid>",
  "bot_id": "<real-bot-uuid>",
  "question": "What are the return policies?",
  "top_k": 5
}
```

Response fields: `answer`, `status`, `citations`, `conversation_id`, `response_time_ms`.

## Technical notes

- Similarity is `1 - cosine_distance` for ChromaDB cosine space; `MIN_SIMILARITY=0.45` is a **starting placeholder**, not a validated threshold.
- Stored citations use document metadata from ingestion; image-only scanned PDFs currently return an explicit no-text error.
- PDF heading extraction is heuristic. Page citations are PDF physical pages, not necessarily printed page numbering.
- Catalogue products and company profile values are indexed separately; adding them makes facts searchable, but the model can still make mistakes. Always validate numerical product prices/availability against the canonical SQL record before production display.
- Company profile sync is manual after each profile edit; the next iteration should automatically handle updates.
- Product editing and re-indexing are available in the connected workspace. Deletion and updates still require stronger transaction/reconciliation logic for production.
- LLM answers are permitted only if the model references one or more available `[S#]` citations. This checks citation IDs, not whether every claim is actually entailed by those excerpts. Medical evaluation is still required.
- Login token is stored in browser sessionStorage solely for alpha convenience. Replace with secure authentication in production.
- There is no public/anonymous chatbot endpoint: the live chat requires an owner token. An embeddable widget is a **future product phase**.

## What do we mean by 'our own API' vs provider API?

**Our own API** = FastAPI endpoints, business logic, document ingestion, vector retrieval, security, chat orchestration and DB. We control it.

**Model API** = Google Gemini/OpenAI token for access to a hosted LLM. The model weights are not ours; the provider handles generation. We can later replace it with a local model (e.g. an open-weight model hosted via an inference server) without changing the client's interface if the adapter is extended.

**Embeddings** = local Sentence Transformers model; no embedding API token is needed in the current setup (initial model download requires internet).

## Roadmap to production

1. Real team roles, organization membership, separate platform admin authentication and invitation flows.
2. PostgreSQL, Alembic migrations, object storage, queues and backups.
3. Permissioned website/FAQ and CSV/JSON catalogue connectors; incremental re-indexing; schema-based company knowledge.
4. Citations with clickable document view, per-claim verification and calibrated abstention/evaluation.
5. Production-ready website widget + domain allowlisting + per-tenant rate limiting + abuse controls.
6. Billing, usage quotas, subscription plan enforcement, token accounting and provider cost controls.
7. Medical-specific safety assessment, governance, data privacy and deployment security review.
8. CI tests, automated metrics dashboards, tracing and evaluation datasets.

