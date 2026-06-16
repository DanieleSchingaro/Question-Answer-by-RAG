#app/rag/ingest.py
"""
Pipeline di ingestion: load -> chunk -> embed -> store
Carica documenti da un singolo file o da un'intera cartella,
li spezza in chunk con sovrapposizione e li indicizza nel vector store di Chroma.
Usa pypdf + pathlib.
"""

from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from app.config import Settings, get_settings
from app.rag.vectorstore import get_vectorstore

SUPPORTED_EXSTENSIONS={".txt", ".md", ".pdf"}

def _load_text_file(path:Path)->list[Document]:
    """Carica un file di testo semplice"""
    text=path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return []
    return [Document(page_content=text, metadata={"source": path.name})]

def _load_pdf_file(path:Path)->list[Document]:
    """Carica un PDF, un Document per pagina"""
    reader=PdfReader(str(path))
    docs: list[Document]=[]
    for page_number, page in enumerate(reader.pages, start=1):
        text=page.extract_text() or ""
        if text.strip():
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name, "page": page_number},
                )
            )
    return docs

def load_documents(path:str|Path)->list[Document]:
    """Carica documenti da un file o da una cartella, in maniera ricorsiva."""
    path=Path(path)
    if path.is_file():
        files=[path]
    elif path.is_dir():
        files=[
            p for p in sorted(path.rglob("*"))
            if p.suffix.lower() in SUPPORTED_EXSTENSIONS
        ]
    else:
        raise FileNotFoundError(f"Percorso non trovato: {path}")
    
    documents:list[Document]=[]
    for f in files:
        ext=f.suffix.lower()
        if ext in {".txt", ".md"}:
            documents.extend(_load_text_file(f))
        elif ext==".pdf":
            documents.extend(_load_pdf_file(f))
    return documents

def split_documents(
        documents:list[Document], settings:Settings|None=None
)->list[Document]:
    """Spezza i documenti in chunk in base ai parametri del .env"""
    settings=settings or get_settings()
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)

def ingest(path:str|Path, settings:Settings|None=None)->dict:
    """Esegue l'intera pipeline e restituisce un riepilogo"""
    settings=settings or get_settings()
    documents=load_documents(path)
    if not documents:
        return {"documents":0, "chunks":0}
    
    chunks=split_documents(documents,settings)
    vectorstore=get_vectorstore(settings)
    vectorstore.add_documents(chunks)

    return {"documents": len(documents), "chunks":len(chunks)}