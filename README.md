# MediRAG AI — Multi-Tenant RAG Chatbot Platform

**An intelligent, source-grounded AI chatbot platform for organizational knowledge, document research, and conversational assistance.**

MediRAG AI is a full-stack Retrieval-Augmented Generation (RAG) platform built with Next.js, FastAPI, SQLAlchemy, ChromaDB, Sentence Transformers, and configurable LLM providers.

The platform enables organizations to manage their knowledgebases, upload documents, maintain product catalogues, configure AI assistants, and interact with their information through natural-language conversations.

Its initial research application focuses on **clinical guideline retrieval and evidence-based medical question answering**.

**Project Status:** Active Development — MediRAG Chat V3

**Repository:** [github.com/145zameerhassanshah/medirag-ai](https://github.com/145zameerhassanshah/medirag-ai)

---

## Key Features

### Organization and Knowledge Management

- User registration and JWT authentication
- Multi-organization workspace
- Organization profile management
- Knowledgebase creation and management
- PDF, DOCX, TXT, and Markdown document ingestion
- Automatic text extraction, chunking, and embeddings
- ChromaDB vector indexing
- Structured product catalogue management
- Company information indexing

### AI Chatbot and Conversations

- Configurable AI assistants
- Natural-language document question answering
- Gemini and OpenAI provider integration
- Source-grounded answers with citations
- Friendly greeting and out-of-scope responses
- Recent conversation context for follow-up questions
- Conversation history and session continuation
- Conversation rename and delete
- Chat history panel inside the Live Chat workspace
- Markdown-formatted responses
- Collapsible source references
- Loading and answer-generation indicators
- Responsive chat interface

### RAG and Retrieval

- Local embeddings using Sentence Transformers
- Semantic similarity search using ChromaDB
- Configurable retrieval thresholds
- Configurable Top-K retrieval
- Source and metadata tracking
- Retrieval candidate filtering
- Heuristic prioritization of relevant guideline passages
- Source-supported answer generation
- Fallback when sufficient evidence is unavailable
- Retrieval evaluation scripts for comparing search configurations

### Optional External Search

MediRAG supports a configurable external web-search integration through Tavily.

The default mode uses organization-owned knowledgebases. External search requires separate API configuration and should be explicitly enabled.

Externally retrieved information must be distinguished from organization documents.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| Data validation | Pydantic |
| Database ORM | SQLAlchemy |
| Authentication | JWT |
| Development database | SQLite |
| Vector database | ChromaDB |
| Embeddings | Sentence Transformers |
| PDF processing | PyMuPDF |
| AI generation | Google Gemini / OpenAI |
| Optional web search | Tavily |

PostgreSQL, production object storage, advanced authorization, and scalable deployment infrastructure are planned enhancements.

---

## System Architecture

```text
                  USER / ORGANIZATION
                           |
                           v
                    Next.js Frontend
                           |
                           v
                     FastAPI Backend
                           |
               Authentication and Validation
                           |
                           v
                  Conversation Processing
                           |
              +------------+------------+
              |                         |
              v                         v
       Greeting / Simple         Knowledge Question
         Response Router                |
              |                         v
              |                  Query Processing
              |                         |
              |                         v
              |                 Embedding Generation
              |                         |
              |                         v
              |                 ChromaDB Retrieval
              |                         |
              |                         v
              |                 Relevance Filtering
              |                         |
              |                         v
              |                Retrieved Evidence
              |                         |
              |                         v
              |                 Gemini / OpenAI
              |                         |
              +------------+------------+
                           |
                           v
                  Grounded AI Response
                           |
                           v
               Citations and Chat History
```

Optional web search is handled separately when enabled and configured.

---

## Project Structure

```text
medirag-ai/
|
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- tests_smoke.py
|   |-- evaluate_retrieval.py
|   |-- .env.example
|   |-- storage/             # Local data, ignored by Git
|
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |   |   |-- live/
|   |   |   |   |-- page.tsx
|   |   |-- components/
|   |-- package.json
|   |-- .env.example
|
|-- README.md
|-- .gitignore
```

Some development and evaluation files may be maintained locally and are not necessarily included in every repository revision.

---

## Getting Started

### Prerequisites

- Python 3.12 recommended
- Node.js compatible with the installed Next.js version
- npm
- Git
- Google Gemini API key or OpenAI API key

### 1. Clone Repository

```bash
git clone https://github.com/145zameerhassanshah/medirag-ai.git
cd medirag-ai
```

### 2. Backend Setup

Open PowerShell in the `backend` directory.

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

If PowerShell blocks activation, for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### 3. Backend Environment Variables

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Configure `backend/.env`:

```env
DATABASE_URL=sqlite:///./medirag.db

JWT_SECRET=YOUR_LONG_RANDOM_SECRET

LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_PRIVATE_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.1-flash-lite

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

MIN_SIMILARITY=0.45

CORS_ORIGINS=http://localhost:3000

WEB_SEARCH_ENABLED=false
```

The Gemini model shown above was successfully tested during local development. Model availability and quotas depend on the provider and account.

Generate a JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated secret into `.env`.

**Never commit `.env` files, API keys, or JWT secrets.**

### 4. Optional Web Search

To enable the Tavily integration, configure:

```env
WEB_SEARCH_ENABLED=true
TAVILY_API_KEY=YOUR_PRIVATE_TAVILY_API_KEY
```

A valid Tavily API key is required. Keep external search disabled for document-only testing.

### 5. Start Backend

```powershell
python -m py_compile main.py

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend API documentation:

`http://127.0.0.1:8000/docs`

Health endpoint:

`http://127.0.0.1:8000/health`

### 6. Frontend Setup

Open another terminal:

```powershell
cd frontend

npm install

Copy-Item .env.example .env.local
```

Configure the API address if needed:

```env
NEXT_PUBLIC_RAG_API_BASE_URL=http://127.0.0.1:8000
```

Start the frontend:

```powershell
npm run dev
```

Open the application:

`http://localhost:3000/live`

---

## How to Use MediRAG

1. Register an account or sign in.
2. Create or select an organization.
3. Configure the organization profile.
4. Create a knowledgebase.
5. Upload and index authorized documents.
6. Create an AI assistant connected to the knowledgebase.
7. Open Live Chat.
8. Ask a question about the indexed information.
9. Review the AI answer and supporting citations.
10. Open a previous conversation to continue the session.

For example:

**Question:** What does WHO recommend about starting antihypertensive treatment?

**Expected behavior:** The chatbot retrieves relevant passages from the uploaded WHO guideline, generates an answer, and displays supporting document references.

If sufficient evidence is unavailable, the assistant should avoid inventing an answer.

---

## Clinical RAG Research

The original research use case evaluates a medical guideline assistant using public WHO hypertension guidance.

During local development, the WHO hypertension guideline was indexed into **208 vector chunks**.

This demonstrates successful ingestion and indexing, but does not by itself prove answer correctness or retrieval accuracy.

### Retrieval Quality Experiments

The evaluation workflow compares:

- Top-K: 3, 5, and 10
- Similarity thresholds: 0.30, 0.45, and 0.60
- Clinical and unrelated test questions
- Retrieved document passages
- Similarity scores
- Page and section metadata
- Retrieval latency

Experiments identified weaknesses including title-only passages receiving high similarity scores, indirect evidence retrieval, and answer-bearing passages being missed for some queries.

These findings motivated retrieval filtering and conversation-aware search improvements.

### Evaluation Metrics

| Metric | Purpose |
|---|---|
| Precision@K | Proportion of retrieved results that are relevant |
| Recall@K | Proportion of known relevant results retrieved |
| MRR | Ranking quality of the first relevant result |
| Answer correctness | Comparison with reference answers |
| Faithfulness | Whether generated claims are supported |
| Citation accuracy | Correct source and page references |
| Fallback accuracy | Handling of unsupported questions |
| Latency | Retrieval and generation response time |

Manual reference annotations are required before reporting reliable quantitative retrieval accuracy.

---

## Security and Privacy

MediRAG includes basic authentication and company ownership checks.

Additional work is required before use with sensitive customer or clinical records:

- Role-based access control
- Multi-user team permissions
- Tenant-isolation testing
- Request rate limiting
- Secure session management
- API key and secret management
- Prompt-injection defenses
- File upload validation
- Encryption and secure storage
- Audit logs
- HTTPS deployment
- Backup and recovery
- Data retention and deletion policies
- Compliance review appropriate to the deployment

Only public or properly authorized documents should be used during development.

---

## Known Limitations

MediRAG is under active development.

- AI answers are not guaranteed to be accurate.
- Retrieved chunks may be semantically similar but not sufficient to answer a question.
- PDF heading extraction is heuristic.
- Scanned documents require OCR support.
- Multi-turn context is limited and requires further evaluation.
- Clinical citation and answer accuracy are not fully validated.
- LLM response latency depends on model availability, network performance, and prompt size.
- Web-search results require their own source-quality checks.
- Complete message editing and answer regeneration are not yet verified.
- Advanced token usage analytics, billing, and quotas are not fully implemented.
- Production security, monitoring, and automated deployment require further work.

---

## Development Roadmap

### Phase 1 — Core Platform

- Authentication and organization management
- Document ingestion
- Embedding generation
- Vector retrieval
- Knowledgebase-connected assistants
- Grounded answer generation

### Phase 2 — Conversational Experience

- Improved Live Chat interface
- Conversation history panel
- Conversation rename/delete
- Markdown rendering
- Source presentation
- Friendly response handling
- Limited multi-turn context

### Phase 3 — Retrieval and Quality

- Better document chunking
- Hybrid semantic and keyword search
- Reranking
- Evaluation datasets
- Faithfulness checks
- Retrieval quality monitoring

### Phase 4 — SaaS Capabilities

- Secure embeddable chatbot widget
- Organization team roles
- Visitor sessions
- Usage and token accounting
- API rate limiting
- Subscription and billing infrastructure
- Human handoff
- Multi-language support
- Admin analytics

### Phase 5 — Production Infrastructure

- PostgreSQL and object storage
- Background processing
- Scalable vector infrastructure
- Automated testing and CI/CD
- Monitoring and alerting
- Security audits
- Deployment documentation

These phases represent development priorities, not guarantees that all listed features are complete.

---

## Medical Disclaimer

MediRAG AI is a research and development application intended to help users explore and retrieve information from authorized documents.

The clinical guideline assistant is **not a medical device** and must not be used as a substitute for professional diagnosis, treatment decisions, emergency services, or qualified clinical judgment.

Medical recommendations must be checked against the original source documents and current clinical guidance.

---

## Project Status

**MediRAG AI — Active Development (Chat V3)**

The application includes a working full-stack RAG foundation, organization-based knowledge management, source-grounded document question answering, and an evolving conversational interface.

The current development focus is retrieval accuracy, natural multi-turn conversation, response speed, source verification, and production-oriented SaaS capabilities.
