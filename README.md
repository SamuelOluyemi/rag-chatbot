# AI Knowledge Assistant — RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask natural-language questions about their contents.

The application uses semantic search to retrieve relevant document passages and a locally hosted Large Language Model (LLM) to generate context-grounded answers.

This project demonstrates the design, development, containerization, deployment, and operation of an AI-powered application using open-source tools and Google Cloud infrastructure.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Security and Reliability](#security-and-reliability)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)

## Features

- **PDF document ingestion:** Upload PDF documents and extract their text.
- **Semantic search:** Retrieve relevant passages using vector embeddings and similarity search.
- **Context-grounded answers:** Generate responses using information retrieved from uploaded documents.
- **Local LLM inference:** Run Llama 3.2 through Ollama without depending on a paid external LLM API.
- **Vector storage:** Store document embeddings using PostgreSQL and pgvector.
- **Document deduplication:** Use SHA-256 file hashing to detect duplicate uploads.
- **Source information:** Return document and chunk references associated with retrieved passages.
- **REST API:** Expose document upload, chat, and health-check endpoints through FastAPI.
- **Containerization:** Use Docker and Docker Compose to manage application infrastructure.
- **Cloud deployment:** Host the application on a Google Compute Engine virtual machine.

## Architecture

The application follows a modular architecture that separates the frontend, API, document-processing pipeline, retrieval system, database, and language model.

### High-level architecture

```text
                         USER
                           |
                           v
                      Web Browser
                           |
                           v
                     React + Vite
                       Frontend
                           |
                           v
                         Nginx
                    Web Server / Proxy
                           |
                           v
                    FastAPI Backend
                           |
              +------------+------------+
              |                         |
              v                         v
        RAG / Retrieval            Ollama Service
           Pipeline                     |
              |                         v
              |                    Llama 3.2 3B
              |
        +-----+------+
        |            |
        v            v
    Embedding    PostgreSQL
      Model       + pgvector
        |            |
        +------------+
              |
              v
       Retrieved Context
              |
              v
        Generated Answer
              |
              v
          Frontend
```

### Application components

| Component             | Responsibility                                |
| --------------------- | --------------------------------------------- |
| React                 | Interactive user interface                    |
| Vite                  | Frontend development and production builds    |
| FastAPI               | Backend REST API                              |
| Uvicorn               | ASGI application server                       |
| PyMuPDF               | PDF text extraction                           |
| Sentence Transformers | Text and query embedding generation           |
| PostgreSQL            | Relational data storage                       |
| pgvector              | Vector storage and similarity search          |
| SQLAlchemy            | Python database ORM                           |
| Alembic               | Database schema migrations                    |
| Ollama                | Local LLM serving and inference               |
| Llama 3.2 3B          | Context-grounded answer generation            |
| Docker                | Application containerization                  |
| Docker Compose        | Container orchestration                       |
| Nginx                 | Static frontend hosting and API reverse proxy |
| Google Compute Engine | Cloud virtual machine hosting                 |
| Ubuntu                | Production server operating system            |

## How It Works

The application implements two main workflows: document ingestion and question answering.

### 1. Document ingestion

When a user uploads a PDF:

1. FastAPI receives the uploaded document.
2. The file-processing service validates the upload and calculates its SHA-256 hash.
3. Duplicate documents are detected to prevent redundant uploads.
4. PyMuPDF extracts the document's text.
5. The chunking service divides the extracted text into smaller sections.
6. Sentence Transformers generates a numerical embedding for each chunk.
7. SQLAlchemy stores document metadata and chunk information in PostgreSQL.
8. pgvector stores the corresponding embeddings for semantic retrieval.

### 2. Question answering

When a user submits a question:

1. The frontend sends the question to the FastAPI chat endpoint.
2. The embedding service converts the question into a vector.
3. The retrieval service performs cosine-similarity search against stored document embeddings.
4. Relevant document chunks are retrieved from PostgreSQL.
5. The RAG service combines the question and retrieved passages into a prompt.
6. Ollama sends the prompt to the locally hosted Llama 3.2 model.
7. The language model generates an answer using the supplied document context.
8. FastAPI returns the generated answer and source information to the frontend.

The system instructs the language model to answer using the retrieved context and avoid introducing unsupported information.

The current retrieval implementation prioritizes the user's most recently uploaded document.

## Technology Stack

### Frontend

**React and Vite**

React provides the component-based user interface, while Vite provides the development server and production build tooling.

### Backend

**Python and FastAPI**

FastAPI handles HTTP requests, document uploads, application services, and communication between the retrieval pipeline, database, and language model.

**Uvicorn** serves the FastAPI application using the ASGI interface.

### Document processing

**PyMuPDF**

Extracts text from uploaded PDF documents.

**Sentence Transformers — all-MiniLM-L6-v2**

Converts text into 384-dimensional embeddings.

The embedding model supports semantic retrieval; it is separate from the language model responsible for generating answers.

### Database and vector search

**PostgreSQL 17**

Stores users, document metadata, and document chunks.

**pgvector**

Extends PostgreSQL with vector data types and similarity-search operations.

Cosine distance is used to rank document passages according to their semantic similarity to a user's question.

### Language model

**Ollama and Llama 3.2 3B**

Ollama provides a local inference server for running the language model.

Llama 3.2 3B generates responses using retrieved document context. This avoids requiring a paid hosted LLM API for normal answer generation.

Generation settings currently include a 256-token output limit and a temperature of 0.2.

### Infrastructure

**Docker and Docker Compose** provide containerized application infrastructure.

**Nginx** serves the production frontend and forwards API requests to FastAPI.

**Google Compute Engine** provides the cloud virtual machine.

**Ubuntu Linux** provides the production operating system.

## Project Structure

```text
rag-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── chat.py
│   │   │       └── documents.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── services/
│   │   │   ├── chunking_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── file_service.py
│   │   │   ├── generation_service.py
│   │   │   ├── ingestion_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── rag_service.py
│   │   │   └── retrieval_service.py
│   │   │
│   │   └── main.py
│   │
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   └── tests/
│       ├── test_api.py
│       ├── test_chunking_service.py
│       ├── test_embedding_service.py
│       ├── test_file_service.py
│       ├── test_generation_service.py
│       ├── test_pdf_service.py
│       ├── test_rag_service.py
│       └── test_retrieval_service.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── .dockerignore
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

Runtime data, environment files, uploaded documents, virtual environments, and generated model artifacts are excluded from version control.

## Local Development

### Prerequisites

Install the following tools:

- Python 3.12 or later
- uv
- Node.js and npm
- Docker Desktop with Docker Compose
- Ollama

### 1. Clone the repository

```bash
git clone https://github.com/SamuelOluyemi/rag-chatbot.git

cd rag-chatbot
```

### 2. Install backend dependencies

The project uses `pyproject.toml` and `uv.lock` to manage Python dependencies.

```bash
uv sync --dev
```

### 3. Start PostgreSQL and pgvector

Start the database service:

```bash
docker compose up -d db
```

The local database is exposed on port `5433`, with PostgreSQL listening on port `5432` inside its container.

### 4. Install and start Ollama

Install Ollama for your operating system, then download the model:

```bash
ollama pull llama3.2:3b
```

Ensure the Ollama service is running and accessible to the backend.

For a local backend process, the default API endpoint is:

```text
http://localhost:11434/api/generate
```

### 5. Configure environment variables

Create the backend environment file at:

```text
backend/.env
```

Configure the database connection and Ollama endpoint according to the application's configuration.

Example connection values:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/ragchatbot

OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:3b
```

The generation service defaults to the local Ollama endpoint and Llama 3.2 3B when these Ollama variables are not supplied.

Keep environment files and credentials out of version control.

### 6. Run database migrations

From the project root:

```bash
uv run alembic upgrade head
```

### 7. Start the backend

From the project root:

```bash
uv run uvicorn app.main:app --app-dir backend --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 8. Start the frontend

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Configure the frontend API base URL for the local backend using the frontend's supported environment configuration.

Vite will display the local development URL in the terminal.

## Configuration

The application uses environment variables for service connections and runtime configuration.

| Variable         | Purpose                        |
| ---------------- | ------------------------------ |
| `DATABASE_URL`   | PostgreSQL connection string   |
| `OLLAMA_API_URL` | Ollama generation API endpoint |
| `OLLAMA_MODEL`   | Ollama model name              |

Default LLM configuration:

```text
Model: llama3.2:3b
API endpoint: http://localhost:11434/api/generate
Output limit: 256 tokens
Temperature: 0.2
Keep-alive: 30 minutes
```

In production, the backend uses the Ollama endpoint configured for communication with the VM host from inside Docker.

## API Endpoints

| Method | Endpoint                | Description                              |
| ------ | ----------------------- | ---------------------------------------- |
| GET    | `/health`               | Application health check                 |
| POST   | `/api/documents/upload` | Upload and process a document            |
| POST   | `/api/chat/`            | Submit a question and retrieve an answer |

Interactive FastAPI documentation is available at `/docs`.

## Testing

The backend uses pytest.

Run the test suite from the project root:

```bash
uv run pytest
```

The current test suite contains 29 tests covering:

- API functionality
- Text chunking
- Embedding generation
- File processing
- PDF extraction
- RAG processing
- Document retrieval

**Latest verified test result:** 29 passed.

## Production Deployment

The application is deployed on Google Cloud Platform using Google Compute Engine.

### Production infrastructure

| Component        | Configuration                          |
| ---------------- | -------------------------------------- |
| Cloud provider   | Google Cloud Platform                  |
| Compute service  | Google Compute Engine                  |
| Region           | us-central1                            |
| Zone             | us-central1-c                          |
| Operating system | Ubuntu 26.04 LTS                       |
| Virtual machine  | Custom E2 instance                     |
| CPU              | 2 vCPUs                                |
| Memory           | Approximately 14.5 GB                  |
| Storage          | 30 GB balanced persistent disk         |
| Web server       | Nginx                                  |
| Backend runtime  | Docker container                       |
| Database         | PostgreSQL 17 with pgvector            |
| LLM service      | Ollama on the VM host                  |
| Frontend         | React production build served by Nginx |

### Production request routing

Nginx listens on HTTP port 80.

- Requests to `/` serve the compiled React frontend.
- Requests to `/api/` are forwarded to FastAPI on `127.0.0.1:8000`.

The backend is bound to the VM's loopback interface rather than being directly exposed to public traffic.

PostgreSQL runs in a Docker container with persistent storage.

Ollama runs as a host-level system service and provides model inference to the backend through the Docker host gateway.

The production deployment uses the following separation:

| Service               | Deployment location                |
| --------------------- | ---------------------------------- |
| Nginx                 | Google Compute Engine host         |
| React frontend        | Built static files served by Nginx |
| FastAPI               | Docker container                   |
| PostgreSQL + pgvector | Docker container                   |
| Ollama                | Google Compute Engine host         |

### Deployment workflow

The general deployment workflow is:

1. Update the application source code.
2. Pull the latest approved changes onto the VM.
3. Build the frontend production assets.
4. Rebuild and restart the backend container when backend code or dependencies change.
5. Apply database migrations when the schema changes.
6. Ensure Nginx serves the latest frontend build.
7. Verify the health endpoint and test document upload and question answering.

Production secrets and environment configuration are maintained on the VM rather than committed to GitHub.

The current deployment uses HTTP. HTTPS and managed TLS certificates remain future improvements.

## Security and Reliability

Security and operational reliability are important considerations for a document-processing application.

Current implementation includes:

- User-to-document ownership relationships in the database.
- SHA-256 file hashing for duplicate detection.
- Database migrations managed through Alembic.
- Backend service binding to localhost in production.
- Persistent database storage.
- Environment-based configuration for service connections.
- Exclusion of environment files, uploaded documents, and generated artifacts from version control.

The production deployment is an evolving portfolio environment, not yet a hardened multi-user production service.

Before handling sensitive documents or real users, additional work is required around HTTPS, authentication, authorization, upload restrictions, secret management, backups, and monitoring.

## Current Limitations

- PDF ingestion is the primary supported document workflow.
- LLM inference runs locally on CPU-based cloud infrastructure and can take significant time.
- Retrieval currently prioritizes the most recently uploaded document rather than providing a full document-selection interface.
- The production application currently runs on a single virtual machine.
- HTTPS and production-grade authentication still require implementation.
- Answer accuracy depends on document quality, chunking, retrieval relevance, and model capabilities.

## Future Improvements

Potential development areas include:

- HTTPS with managed TLS certificates.
- User authentication and authorization.
- A document-management interface with explicit document selection.
- Search across multiple uploaded documents.
- Improved retrieval with hybrid search and reranking.
- Streaming LLM responses.
- Better generation performance and inference optimization.
- Automated deployment through GitHub Actions.
- Infrastructure provisioning with Terraform.
- Application monitoring, structured logging, and alerting.
- Automated database backups and recovery procedures.
- Improved evaluation of retrieval accuracy and answer faithfulness.

## Project Goals

This project explores practical implementation of:

- Retrieval-Augmented Generation architectures.
- Local language model deployment.
- Semantic search and vector databases.
- REST API development.
- Relational database design.
- Docker-based application deployment.
- Linux server administration.
- Reverse proxy configuration.
- Google Cloud virtual machine deployment.
- Production troubleshooting and performance optimization.

The goal is to build a practical, understandable, and extensible AI application while developing hands-on experience with backend engineering, AI infrastructure, databases, and cloud operations.
