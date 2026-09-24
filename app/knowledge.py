from pathlib import Path
import re
from typing import Any

class KnowledgeBase:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.chunks = []
        self.files = {}

    def load(self):
        self.chunks = []
        self.files = {}
        for path in self.upload_dir.iterdir():
            if path.is_file() and path.suffix.lower() in {".pdf", ".docx", ".txt"}:
                try:
                    self.index_file(path, path.name)
                except Exception:
                    continue

    def document_count(self):
        return len(self.files)

    def documents(self):
        return [{"name": name, "chunks": count} for name, count in self.files.items()]

    def extract_text(self, path: Path):
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if suffix == ".docx":
            from docx import Document
            document = Document(str(path))
            return "\n".join(p.text for p in document.paragraphs)
        raise ValueError("Unsupported file type")

    def index_file(self, path: Path, display_name: str):
        text = self.extract_text(path)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            raise ValueError("The document contains no readable text.")
        chunks = self.chunk_text(text)
        self.chunks = [c for c in self.chunks if c["source"] != display_name]
        for chunk in chunks:
            self.chunks.append({"source": display_name, "text": chunk})
        self.files[display_name] = len(chunks)

    def chunk_text(self, text, size=900, overlap=150):
        if len(text) <= size:
            return [text]
        result = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            result.append(text[start:end])
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
        return result

    def search(self, query: str, limit=5):
        if not self.chunks:
            return []
        query_terms = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        scored = []
        for item in self.chunks:
            words = re.findall(r"[a-zA-Z0-9]+", item["text"].lower())
            word_set = set(words)
            overlap = len(query_terms & word_set)
            phrase_bonus = 0
            normalized = item["text"].lower()
            if query.lower() in normalized:
                phrase_bonus = 5
            score = overlap + phrase_bonus
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]
