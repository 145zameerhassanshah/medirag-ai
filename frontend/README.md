# MediRAG AI — Responsive SaaS Frontend (Phase 1)

A runnable **Next.js + TypeScript** UI prototype for a future multi-tenant, domain-independent RAG chatbot product. This is the first *frontend* phase, built separately from the existing Day 1–4 clinical Python project.

## Included screens

**Client admin:** Overview, Knowledgebases, Documents, AI Chatbots, Chat Playground, Conversations, Analytics, Integrations, AI Settings.

**Super admin:** Platform Overview, Organizations, Billing Plans, System Activity.

**Customer-facing preview:** Website Widget Preview.

The UI is responsive on desktop, tablet and mobile. It includes sidebar navigation, modals, create/delete of local preview data, search, filters, bot selection, chat history, settings controls, local JSON export, a document-file picker, and user feedback states.

## Important: What actually works

- The UI is *interactive*; knowledgebases, bots, conversations, document **metadata only**, and settings are saved in browser `localStorage`.
- Demo organizations and plans are **fictional** placeholders. Admin role switching is a preview toggle, **not authentication or authorization**.
- The documents picker **does not upload, persist file bytes, extract text, or create embeddings**; names and sizes only are saved locally.
- Chat without a backend **does not fabricate medical answers**: it explains that API integration is pending.
- The optional API adapter sends `POST {NEXT_PUBLIC_RAG_API_BASE_URL}/api/chat` and displays actual responses and citations if your backend matches the API contract.
- Real RAG, secure login, workspace isolation, server database, PDF ingestion, vector storage, LLM calls, analytics instrumentation, subscription billing and actual widget.js embedding **are not yet implemented**.

## Requirements

Node.js **20.9+** with npm. Python is not needed to launch the UI preview.

## Run on Windows PowerShell

```powershell
# Extract this project in a separate folder, then:
cd medirag-ui
npm install
npm run dev
```

Open http://localhost:3000

If your Python/Streamlit app is running on port 8501, it can stay there; Next.js runs separately on port 3000.

## Optional API mode

1. Copy `.env.example` to `.env.local`.
2. Set `NEXT_PUBLIC_RAG_API_BASE_URL=http://127.0.0.1:8000` **only after** implementing the Python FastAPI backend.
3. Restart `npm run dev`.
4. Chat sends the following request:

```json
{
  "question":"What does this guideline recommend?",
  "bot_id":"bot-care",
  "knowledgebase_id":"kb-health",
  "conversation_id":"conversation-id"
}
```

Expected response:

```json
{
  "answer":"A source-grounded answer from your real RAG engine.",
  "citations":[{"filename":"example.pdf","page_start":12,"section":"Monitoring"}]
}
```

**Security:** Never put model/API secrets into a `NEXT_PUBLIC_` variable. Use backend-only secrets. Before production, implement user authentication, server-enforced tenant isolation, validation of citation metadata, tenant-scoped retrieval, CSRF protection where applicable, limits, safe document handling, and monitoring.

## Recommended next phases

1. Implement FastAPI with real PDF extraction, page/section metadata and ChromaDB indexing, reusing Day 1/2 Python modules.
2. Implement real LLM provider integration, relevance thresholds, refusal/fallback, verified source citations, and medical safety constraints.
3. Replace localStorage with authenticated, tenant-scoped server storage (PostgreSQL); add document add/remove, chat history and indexing jobs.
4. Implement website widget SDK, client configuration, usage analytics, paid plans and production deployment.
5. Evaluate retrieval Recall@K, citation accuracy, answer faithfulness, latency and unsupported-answer behavior.

## Project structure

```
medirag-ui/
├── src/app/layout.tsx
├── src/app/globals.css
├── src/app/[[...path]]/page.tsx
├── src/components/Workbench.tsx
├── .env.example
├── package.json
└── README.md
```

**Note:** This UI supports any **configured domain category** as a preview; domain-general production behavior requires an actual multi-tenant RAG backend.
