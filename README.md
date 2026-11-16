
# MediRAG AI — Dynamic RAG Chatbot Platform

A full-stack, multi-organization Retrieval-Augmented Generation (RAG) chatbot application built with Next.js, FastAPI, SQLAlchemy, ChromaDB, Sentence Transformers, and configurable large language model APIs.

MediRAG AI allows organizations to manage knowledgebases, upload documents, configure AI assistants, and ask questions grounded in their own information.

The initial research use case focuses on clinical guidelines and evidence-based medical question answering.

## Features

- User registration and authentication
- Organization and company profile management
- Knowledgebase creation
- PDF, DOCX, TXT, and Markdown document ingestion
- Automatic text extraction and chunking
- Local embedding generation using Sentence Transformers
- ChromaDB vector storage and similarity search
- Configurable Gemini or OpenAI answer generation
- Source citations with document, page, and section metadata
- Relevance filtering and unsupported-answer fallback
- Empty-query validation
- Product catalogue management
- Saved chat conversations and messages
- Responsive Next.js admin workspace

## Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Responsive CSS

### Backend
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- JWT authentication

### AI and Retrieval
- Sentence Transformers
- ChromaDB
- Cosine similarity search
- Google Gemini or OpenAI API
- PyMuPDF for PDF extraction

### Storage
- SQLite for local development
- ChromaDB for vector embeddings
- Local document storage

PostgreSQL, production object storage, and additional access controls are planned improvements.

## RAG Architecture

```text
User Question
     |
     v
Next.js Chat Interface
     |
     v
FastAPI Backend
     |
     v
Input Validation
     |
     v
Question Embedding
     |
     v
ChromaDB Similarity Search
     |
     v
Relevance Filtering
     |
     v
Retrieved Document Context
     |
     v
Gemini / OpenAI
     |
     v
Source-Grounded Answer
     |
     v
Citations + Chat History
```

## Project Structure

```text
medirag_fullstack/
|
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- .env.example
|   |-- storage/           # Local data; excluded from Git
|
|-- frontend/
|   |-- src/
|   |   |-- app/
|   |-- package.json
|   |-- .env.example
|
|-- README.md
|-- .gitignore
```

## Local Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/medirag-ai.git
cd medirag-ai
```

### 2. Configure the Backend

Recommended Python version: 3.12.

On Windows PowerShell:

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

Create the environment configuration:

```powershell
Copy-Item .env.example .env
```

Configure the required variables:

```env
DATABASE_URL=sqlite:///./medirag.db

JWT_SECRET=GENERATE_A_LONG_RANDOM_SECRET

LLM_PROVIDER=gemini
GEMINI_API_KEY=YOUR_PRIVATE_API_KEY
GEMINI_MODEL=gemini-2.5-flash

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

MIN_SIMILARITY=0.45

CORS_ORIGINS=http://localhost:3000
```

Generate a JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated secret into `backend/.env`.

Never commit API keys or `.env` files to GitHub.

### 3. Start the Backend

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend API documentation:

http://127.0.0.1:8000/docs

Health endpoint:

http://127.0.0.1:8000/health

### 4. Configure the Frontend

Open another terminal:

```powershell
cd frontend

npm install

Copy-Item .env.example .env.local

npm run dev
```

Frontend:

http://localhost:3000/live

## Usage

1. Register or sign in.
2. Create an organization/company profile.
3. Create a knowledgebase.
4. Upload and index an authorized document.
5. Create a chatbot connected to the knowledgebase.
6. Open the chat interface.
7. Ask questions about indexed information.
8. Review responses and source citations.
9. Check saved conversation history.

## Medical RAG Research Use Case

The initial medical research workflow uses public clinical guideline documents.

A local development test indexed the WHO hypertension guideline into 208 text chunks.

This confirms a recorded ingestion result, but does not establish retrieval accuracy, medical answer correctness, or production readiness.

### Research Requirements

- Clinical guideline ingestion
- Text chunking and embedding generation
- Similarity-based passage retrieval
- Context-grounded answer generation
- Document, page, and section citations
- Relevance thresholds
- Invalid and empty query handling
- Unsupported-question fallback
- Retrieval and answer evaluation
- Response-time measurement
- Documented limitations

## Evaluation Methodology

A complete evaluation requires a labeled medical question dataset with manually verified reference passages and answers.

Recommended metrics:

| Metric | Purpose |
|---|---|
| Recall@K | Whether relevant passages are retrieved |
| Precision@K | Relevance of retrieved passages |
| MRR | Rank of the first relevant result |
| Answer correctness | Accuracy against reference answers |
| Faithfulness | Whether claims are supported by sources |
| Citation accuracy | Correct document, page, and section |
| Fallback accuracy | Rejection of unsupported questions |
| Response latency | Processing and generation time |

The current code provides basic retrieval and per-request timing. A complete automated evaluation pipeline is not yet verified.

## Security Considerations

The application includes basic JWT authentication and organization ownership checks.

Before production deployment, additional security work is required:

- Role-based access control
- Tenant isolation tests
- Rate limiting
- Secure API key management
- Input and upload security
- Prompt-injection testing
- Audit logging
- HTTPS
- Database backups
- Data retention and deletion policies
- Appropriate privacy and medical compliance review

Use public or explicitly authorized, non-sensitive documents for local research testing.

## Known Limitations

1. Scanned PDFs require OCR support.
2. PDF heading detection is heuristic.
3. Similarity thresholds require calibration.
4. Retrieved evidence may not always be relevant.
5. LLM-generated answers may contain unsupported claims.
6. Citation identifiers alone do not prove factual accuracy.
7. Multi-turn conversational reasoning needs improvement.
8. Automated medical evaluation is incomplete.
9. Production security controls need additional development.
10. Super Admin, billing, and advanced team permissions are not fully implemented.

## Future Improvements

- PostgreSQL migration
- Hybrid search and reranking
- Improved citation grounding
- Source document preview
- Conversation-aware retrieval
- Automated RAG evaluation
- Production-grade multi-tenant permissions
- Website chatbot embedding
- Usage analytics and monitoring
- Background document processing

## Disclaimer

MediRAG AI is a research and development project. Its medical guideline assistant is intended for document exploration and is not a substitute for professional medical diagnosis, treatment, or emergency care.

## Project Status

**Active Development**

Document ingestion, knowledgebase retrieval, and the full-stack application structure are implemented. LLM generation, complete medical evaluation, advanced security, and production deployment require further verification and development.
