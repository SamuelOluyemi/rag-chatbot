# AI Knowledge Assistant (RAG Chatbot)

A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on uploaded documents.

## 🚀 Features
- Upload PDF documents
- Ask questions about the document
- Context-aware AI responses
- FastAPI backend + FAISS vector search

## 🛠 Tech Stack
- Python (FastAPI)
- OpenAI API
- FAISS (vector search)
- Docker
- Deployable to Google Cloud Run

## 📦 Setup

### 1. Clone repo
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot/backend

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add environment variables
cp .env.example .env
# add your OPENAI_API_KEY

### 4. Run locally
uvicorn app.main:app --reload

API runs on:
http://127.0.0.1:8000

## 📂 API Endpoints

### Upload PDF
POST /upload

### Ask Question
POST /ask
{
  "question": "What is this document about?"
}

## 🐳 Docker

docker build -t rag-chatbot .
docker run -p 8080:8080 rag-chatbot

## ☁️ Deployment
- Backend: Google Cloud Run
- Frontend: Vercel

## 📄 Resume Bullet

Built an AI-powered document Q&A system using RAG, FastAPI, and FAISS, deployed on cloud infrastructure to enable context-aware responses from uploaded documents.