#app/rag/vectorstore.py
"""
Vector store ChromaDB persistente.
Collega il modello di embeddings a un database Chroma su disco. Un'unica funzione restituisce l'istanza pronta all'uso,
sia per l'indicizzazione (ingest) sia per il retrieval (query), così la configurazione della collection vive in un solo posto.
"""

from pathlib import Path
from langchain_chroma import Chroma
from app.config import Settings, get_settings
from app.rag.providers import get_embeddings

def get_vectorstore(settings:Settings|None=None)->Chroma:
    """Restituisce un istanza Chroma persistente collegata agli embeddings"""
    settings=settings or get_settings()
    
    #Assicura che la cartella del DB esista
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=get_embeddings(settings),
        persist_directory=settings.chroma_dir,
    )