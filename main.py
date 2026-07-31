from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import google.genai
print("Google GenAI SDK:", google.genai.__file__)

from core.config import settings
from routes.chat import router as chat_router

app = FastAPI(
    title="GlowAI — Skincare Chatbot API",
    description="""
## GlowAI — AI Skincare Consultant

**Stack:** FastAPI · LangGraph · Hugging Face · DuckDuckGo RAG

### LangGraph Pipeline
```
User Message
     ↓
[extract]  — NLP entity extraction (NER)
     ↓
  profile complete?
  NO  → [chat]     — Ask follow-up question
  YES → [search]   — DuckDuckGo RAG
            ↓
        [recommend] — Synthesize product cards
```

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat/` | Main chat endpoint |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API docs |
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


frontend_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "frontend")
print(f"Frontend path: {frontend_path}")
print(f"Frontend exists: {os.path.exists(frontend_path)}")

if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path), name="frontend")



@app.get("/health", tags=["System"])
async def health():
    return {
        "status": "healthy ✅",
        "version": "2.0.0",
        "stack": {
            "framework": "FastAPI 0.115.0",
            "agent": "LangGraph 1.1.6",
            "llm": "Qwen2.5-72B via Hugging Face",
            "rag": "DuckDuckGo Search",
        }
    }


@app.get("/", tags=["System"])
async def root():
    # Serve index.html if it exists
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "app": "GlowAI Skincare API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level="info",
    )
