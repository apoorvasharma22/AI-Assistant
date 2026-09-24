# Intelligent Customer Support AI Assistant

A full-stack customer support assistant built with FastAPI. It accepts PDF, DOCX and TXT company documents, indexes their content, retrieves relevant knowledge and generates grounded answers. It maintains conversation context and escalates questions when the knowledge base cannot answer them.

## Features

- PDF, DOCX and TXT upload
- Document extraction and chunking
- Knowledge-base retrieval
- OpenAI-powered grounded responses
- Conversation context
- Explicit "I don't know" fallback
- Escalation flag for unanswered questions
- Responsive customer-support interface
- Health endpoint
- Document listing endpoint
- API documentation through FastAPI

## Project Structure

```text
customer_support_ai_assistant/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── knowledge.py
│   └── main.py
├── data/
├── static/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

## Run Locally

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
set OPENAI_API_KEY=your_key_here
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## API

### Health

`GET /api/health`

Returns application status and indexed document count.

### Upload

`POST /api/upload`

Multipart form field:

```text
file
```

Supported extensions:

```text
.pdf
.docx
.txt
```

### Documents

`GET /api/documents`

Returns indexed documents.

### Chat

`POST /api/chat`

Request:

```json
{
  "message": "What is the refund policy?",
  "session_id": "optional-session-id"
}
```

Response:

```json
{
  "session_id": "session-id",
  "answer": "Answer from the company documentation.",
  "sources": ["faq.pdf"],
  "escalated": false
}
```

## Environment Variables

```text
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

If no OpenAI key is configured, the application still works with retrieval-based responses.

## Deployment

The application can be deployed to Render using the included `render.yaml`.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

For production document persistence, use object storage or a database/vector store because local deployment disks may be ephemeral.

## Architecture

```text
User
  |
  v
Responsive Web UI
  |
  v
FastAPI Backend
  |
  +--------------------+
  |                    |
  v                    v
Document Upload     Chat Request
  |                    |
  v                    v
PDF/DOCX/TXT       Conversation Memory
  |                    |
  v                    v
Text Extraction     Knowledge Retrieval
  |                    |
  +---------+----------+
            |
            v
       Grounded AI
            |
      +-----+-----+
      |           |
      v           v
   Answer     Escalation
```
