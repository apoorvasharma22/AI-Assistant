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

