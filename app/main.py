import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .knowledge import KnowledgeBase
from .ai import generate_answer

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Intelligent Customer Support AI Assistant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

knowledge_base = KnowledgeBase(UPLOAD_DIR)
sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[str]
    escalated: bool

@app.on_event("startup")
def startup():
    knowledge_base.load()

@app.get("/api/health")
def health():
    return {"status": "ok", "documents": knowledge_base.document_count()}

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    allowed = {".pdf", ".docx", ".txt"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX and TXT files are supported.")
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / safe_name
    content = await file.read()
    destination.write_bytes(content)
    try:
        knowledge_base.index_file(destination, file.filename or safe_name)
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not process document: {exc}")
    return {"message": "Document uploaded and indexed.", "filename": file.filename}

@app.get("/api/documents")
def documents():
    return {"documents": knowledge_base.documents()}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    session_id = request.session_id or uuid.uuid4().hex
    history = sessions.setdefault(session_id, [])
    matches = knowledge_base.search(message, 5)
    answer, sources, escalated = generate_answer(message, history, matches)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    sessions[session_id] = history[-12:]
    return ChatResponse(session_id=session_id, answer=answer, sources=sources, escalated=escalated)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")
