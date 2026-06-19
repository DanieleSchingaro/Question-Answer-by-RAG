#backend/app/main.py
"""
FastAPI: espone la pipeline RAG mediante HTTP.
Endpoint:
    GET /health stato del servizio e provider attivi
    POST /ingest carica e indicizza uno o più documenti 
    POST /query pone una domanda e riceve una risposta + fonti

CORS configurato per frontend Next.js .
"""

import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.rag.chain import answer_question
from app.rag.ingest import SUPPORTED_EXSTENSIONS, ingest
from app.schema import(
    HealtResponse,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    SourceDocument,
)

#Origini autorizzare a chiamare l'API dal browser
#Sviluppo: dev server di Next.js
ALLOWED_ORIGINS=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app=FastAPI(
    title="RAG Question Answering API",
    description=(
        "Sistema di Question Answering basato su RAG con LangChain, ChromaDB "
        "e Google Gemini. Carica documenti e interrogali ottenendo risposte "
        "ancorate al contesto, con citazione delle fonti."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealtResponse)
def health()->HealtResponse:
    """Stato del servizio e provider/modelli attualmente attivi."""
    s=get_settings()
    return HealtResponse(
        llm_provider=s.llm_provider,
        llm_model=s.llm_model,
        embedding_provider=s.embedding_provider,
    )

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(files:list[UploadFile]=File(...))->IngestResponse:
    """Carica uno o più documenti e li indicizza nel vector store."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path=Path(tmp)
        saved=0
        for f in files:
            ext=Path(f.filename or "").suffix.lower()
            if ext not in SUPPORTED_EXSTENSIONS:
                continue
            dest=tmp_path/Path(f.filename).name
            with dest.open("wb") as out:
                shutil.copyfileobj(f.file, out)
            saved+=1

        if saved==0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Nessun file supportato caricato. Estensioni ammesse: "
                    f"{sorted(SUPPORTED_EXSTENSIONS)}"
                ),
            )
        result=ingest(tmp_path)
    
    if result["chunks"]==0:
        raise HTTPException(
            status_code=400,
            detail="Nessun contenuto testuale estraibile dai file caricati.",
        )

    return IngestResponse(
        documents=result["documents"],
        chunks=result["chunks"],
        message=(
            f"Indicizzati {result['chunks']} chunk"
            f"da {result['documents']} documento/i."
        ),
    )

@app.post("/query", response_model=QueryResponse)
def query(request:QueryRequest)->QueryResponse:
    """Pone una domanda al sistema RAG e restituisce una risposta + fonti."""
    result=answer_question(request.question)
    return QueryResponse(
        answer=result["answer"],
        sources=[SourceDocument.from_document(d) for d in result["sources"]],
    )