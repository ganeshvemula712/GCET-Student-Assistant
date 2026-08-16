# GCET Student Assistant
### AI-Powered RAG-Based Academic Assistant for GCET Students

[![Render Deployment](https://img.shields.io/badge/Render-Live_Production-emerald?style=flat&logo=render)](https://gcet-student-assistant-frontend.onrender.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.2-61DAFB.svg?style=flat&logo=react)](https://react.dev/)
[![Tests Passing](https://img.shields.io/badge/Tests-106%2F106_Passed-success.svg?style=flat)](https://github.com/ganeshvemula712/GCET-Student-Assistant)

---

## Project Overview

**GCET Student Assistant** is an AI-powered academic companion designed to help students at Geethanjali College of Engineering and Technology (GCET) access verified institutional information through natural language queries.

The platform integrates a modern **React single-page frontend**, a high-performance **FastAPI backend**, a relational **PostgreSQL database**, and a local **ChromaDB vector database**. It combines retrieval-augmented generation (RAG), intent classification, Google Gemini LLM synthesis, JWT authentication, and role-based access control (RBAC) to deliver grounded, accurate academic answers.

---

## Problem Statement

Higher education students frequently spend excessive time searching through scattered PDF documents, notices, academic regulations, syllabi, timetables, examination schedules, attendance rules, and placement statistics.

GCET Student Assistant resolves this by providing a unified conversational interface that grounds answers strictly in official GCET institutional documents uploaded and verified by administrators.

---

## Key Features

### Student Features
- **Authentication**: Secure email/password login, account registration, and Google Sign-In.
- **Conversational AI Assistant**: Interactive chat interface with real-time response streaming.
- **Intent-Based Answering**: Automatically routes questions to General Knowledge or GCET Document Retrieval.
- **Grounding Protection**: Emits a `Knowledge Base Unavailable` badge when requested GCET information is not present in indexed documents.
- **Conversation Memory**: Maintains chat history while keeping multi-turn context isolated from intent routing.
- **Document Browser**: View indexed institutional documents categorized by department and academic topic.
- **Profile & Settings**: View user details, role permissions, and user preferences.

### Admin Features
- **Role-Based Access Control**: Guarded routes and endpoints accessible exclusively to administrative users.
- **User Management**: View registered students, promote users to Admin, or demote users to Student.
- **User Table Filters**: Search users by name/email, filter by role, and paginate through user records.
- **Document Upload**: Upload PDF documents with category selection, tags, and automated text chunking.
- **Knowledge Base Management**: Delete outdated documents and track active ChromaDB indexing status.
- **Document Inspection**: Preview metadata, active chunks, category classifications, and upload timestamps.

### AI & RAG Features
- **Query Intent Classifier**: Regex and embedding-based intent routing to separate general questions from GCET queries.
- **Vector Similarity Search**: ChromaDB vector store with cosine distance matching (`RELEVANCE_THRESHOLD = 1.45`).
- **Strict Grounding Enforcement**: Prevents hallucinated responses when document evidence is missing.
- **Response Metadata Badges**: Visual indicators for `General Knowledge`, `Verified RAG`, and `Knowledge Base Unavailable`.

---

## RAG Pipeline Architecture

### Document Ingestion Flow
```
Document Upload (Admin)
      │
      ▼
Document Processing (PyMuPDF)
      │
      ▼
Text Extraction & Normalization
      │
      ▼
Text Chunking (Recursive Character Splitter)
      │
      ▼
Embedding Generation (Google Gemini Embeddings)
      │
      ▼
ChromaDB Vector Store (Persistent Storage)
```

### Query Execution Flow
```
User Question
      │
      ▼
Intent Classification & Query Normalization
      │
 ┌────┴─────────────────────────────┐
 │                                  │
 ▼ (General Query)                  ▼ (GCET Document Query)
General Knowledge LLM Path    ChromaDB Vector Retrieval
 │                                  │
 │                            ┌─────┴──────────────────────────────┐
 │                            │ (Chunks Found)                     │ (Zero Chunks / Distance > Threshold)
 │                            ▼                                    ▼
 │                     Relevant Context                    Knowledge Base Unavailable
 │                            │                                    │
 └──────────────────────────► LLM ◄────────────────────────────────┘
                              │
                              ▼
                       Grounded Response
```

---

## Technology Stack

| Domain | Technology / Library | Usage / Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite 8, Tailwind CSS v4 | Responsive UI, SPA routing, styling |
| **Frontend Data** | `@tanstack/react-query`, Axios | Async API state management & HTTP client |
| **Frontend UI** | Lucide React, Framer Motion, Sonner | Icons, micro-animations, toast notifications |
| **Backend** | Python 3.12, FastAPI 0.138, Uvicorn | RESTful API server & async handlers |
| **Database** | PostgreSQL, SQLAlchemy 2.0 | User accounts, sessions, document metadata |
| **Vector Store** | ChromaDB 1.5 | Embeddings storage & vector similarity search |
| **AI / LLM** | Google GenAI SDK (Gemini API) | Embedding generation & grounded answer synthesis |
| **Document Processing**| PyMuPDF, Python-Docx | Text extraction from PDF & DOCX files |
| **Authentication** | PyJWT, Passlib (bcrypt), Google GIS | JWT tokens, password hashing, Google OAuth |
| **Testing** | Pytest, Pytest-Asyncio | Automated backend integration & RAG test suite |
| **Deployment** | Render | Managed Docker Web Service & PostgreSQL DB |

---

## Document Knowledge Base

Documents uploaded by administrators are organized into explicit categories:

- **Academic Regulations**
- **Course Syllabus**
- **Placements**
- **Timetables**
- **Examinations**
- **Attendance**
- **Notices & Circulars**
- **General Academic**

Administrators can attach searchable tags (e.g., `4th-year`, `DS`, `AR25`, `2025-26`) to fine-tune document metadata and simplify categorization.

---

## Security & Role-Based Access Control (RBAC)

- **Student Role**: Access to AI Assistant, document browser, personal profile, settings, and general knowledge capabilities. Restricted from administrative functions.
- **Admin Role**: Complete administrative privileges including user management, role elevation, document upload, category tagging, and knowledge base deletion.
- **Endpoint Authorization**: Protected backend routes enforce JWT bearer token validation and `require_admin` dependency checks.

---

## AI Response Modes

| Mode Indicator | Visual Badge | Trigger Criteria | Behavior |
| :--- | :--- | :--- | :--- |
| **General Knowledge** | Blue Pill Badge | Conceptual or general computer science questions (e.g., *"What is Python?"*) | Responds using general AI knowledge without institutional document citations. |
| **Verified RAG** | Emerald Pill Badge | GCET institutional questions matching indexed documents | Synthesizes response strictly grounded in retrieved ChromaDB text chunks. |
| **Knowledge Base Unavailable** | Amber Pill Badge | GCET institutional questions with no matching uploaded documents | States clearly that information is not available in the GCET Knowledge Base without fabricating answers. |

---

## Automated Test Verification

The backend includes a comprehensive Pytest test suite covering authentication, RAG routing, memory isolation, document ingestion, and category filters.

```bash
$env:PYTHONPATH='.'; .\.venv\Scripts\pytest.exe tests -v
```

```text
====================== 106 passed, 5 warnings in 9.44s ======================
```

- **106/106 Tests Passed** (100% pass rate)
- Intent classification & memory regression tests verified
- Stream response metadata synchronization verified

---

## Responsive Design & SEO

- **Tested Viewports**: Desktop (1920px), Laptop (1366px), Tablet (768px), Mobile (390px).
- **Zero Viewport Scrollbar**: Login card layout formatted to fit standard screens without vertical clipping.
- **SEO Metadata**:
  - `robots.txt` (`Allow: /`, `Sitemap: https://gcet-student-assistant-frontend.onrender.com/sitemap.xml`)
  - `sitemap.xml`
  - Open Graph title, description, and canonical URL configured in `index.html`.

---

## Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL (or local SQLite fallback)

### 1. Repository Setup
```bash
git clone https://github.com/ganeshvemula712/GCET-Student-Assistant.git
cd GCET-Student-Assistant
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
```

Configure `.env` with your environment variables:
```env
APP_NAME=GCET Student Assistant
DATABASE_URL=postgresql://user:password@localhost:5432/gcet_student_assistant
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Start the FastAPI backend server:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend will run at `http://localhost:5173` and connect to the backend at `http://127.0.0.1:8000`.

---

## Project Structure

```text
GCET-Student-Assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers (auth, chat, documents, admin)
│   │   ├── core/         # Security, JWT, database settings, error handlers
│   │   ├── db/           # SQLAlchemy models & database migrations
│   │   ├── schemas/      # Pydantic validation schemas
│   │   └── services/     # RAG pipeline, intent detection, memory, ChromaDB
│   └── main.py           # FastAPI application entrypoint
├── frontend/
│   ├── public/           # Static assets, robots.txt, sitemap.xml
│   └── src/
│       ├── assets/       # Branding assets (gcet-logo.png)
│       ├── components/   # UI components (auth, chat, documents, common)
│       ├── context/      # React AuthContext
│       ├── hooks/        # Custom React Query hooks
│       ├── layouts/      # AuthLayout & ProtectedLayout
│       ├── pages/        # Login, Register, Dashboard, Chat, Documents, Admin, Profile
│       ├── routes/       # AppRoutes & protected route guards
│       ├── services/     # Axios API client & auth service
│       └── main.jsx      # React DOM entrypoint
├── tests/                # Pytest test suite (106 unit & integration tests)
├── .env.example          # Sample environment variables
├── Dockerfile            # Container build specification
├── render.yaml           # Render IaC deployment config
└── requirements.txt      # Python dependencies
```

---

## Production Deployment

The project is live in production on **Render**:

- **Frontend App**: [https://gcet-student-assistant-frontend.onrender.com/](https://gcet-student-assistant-frontend.onrender.com/)

---

## Screenshots

| View | Preview |
| :--- | :--- |
| **Login Workspace** | ![Login Workspace](frontend/src/assets/gcet-logo.png) |
| **Student Dashboard** | *(Available in live demo)* |
| **AI Assistant (RAG Response)** | *(Available in live demo)* |
| **Knowledge Base Documents** | *(Available in live demo)* |
| **Admin User Management** | *(Available in live demo)* |

---

## Demonstration Walkthrough

1. **Student Login**: Student signs in using institutional email or Google OAuth.
2. **General Query**: Student asks *"What is Python?"* → Assistant responds via General Knowledge mode.
3. **Institutional RAG Query**: Student asks *"time table for 4th year 1sem"* → Query routed to ChromaDB vector search → Grounded timetable content returned with Verified RAG badge.
4. **Missing Knowledge Query**: Student asks about unindexed topics → Assistant returns clear `Knowledge Base Unavailable` notice without inventing data.
5. **Admin Management**: Administrator logs in, uploads a new academic document with category and tags, and updates user roles.

---

## Limitations

- **Knowledge Boundary**: Answers are strictly constrained by documents uploaded to ChromaDB by administrators.
- **Document Quality**: Text extraction quality depends on input PDF formatting. Scan-only PDFs without OCR text layers require pre-OCR processing.
- **Academic Project Scope**: Designed as an academic project demonstration for portfolio evaluation.

---

## Future Improvements

- OCR pipeline integration for scanned image PDFs.
- Source chunk paragraph highlighting & page-number citations.
- Support for multi-lingual query handling.
- Hybrid BM25 + dense vector reranking.
