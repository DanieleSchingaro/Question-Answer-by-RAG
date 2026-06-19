#backend/app/config.py
"""
Configurazione dell'applicazione.
Tutte le impostazioni vengono lette dalle variabili d'ambiente (o da un file
'.env' locale). Nessun valore hardcoded viene sparso nel resto del codice.
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    #LLM
    llm_provider:Literal["gemini", "ollama"]="gemini"
    llm_model:str="gemini-2.5-flash"
    llm_temperature:float=0.1

    #Embeddings
    embedding_provider:Literal["gemini", "huggingface"]="gemini"
    embedding_model:str="gemini-embedding-001"

    #Google Gemini
    google_api_key:str|None=None

    #Ollama
    ollama_base_url:str="http://localhost:11434"

    #Storage
    chroma_dir:str="./data/chroma"
    collection_name:str="rag_documents"

    #Chunking & retrieval
    chunk_size:int=100
    chunk_overlap:int=150
    retrieval_k:int=4

@lru_cache
def get_settings()->Settings:
    """Restituisce un'istanza Settings cachata (letta una volta, riusata ovunque)."""
    return Settings()