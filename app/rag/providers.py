#app/rag/providers.py
"""
Factory per i modelli LLM e di embedding.

Centralizza la scelta del provider in un unico punto: il resto dell'app dipende
solo dalle interfacce astratte di LangChain (BaseChatModel, Embeddings), mai da
un fornitore concreto. Cambiare provider = cambiare un valore nel .env.

Gli import dei provider opzionali (Ollama, HuggingFace) sono "lazy": vengono
eseguiti solo se quel provider è effettivamente selezionato, così il modulo non
richiede pacchetti che non hai installato.
"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from app.config import Settings, get_settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama #type:ignore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings #type:ignore

def get_llm(settings:Settings|None=None)->BaseChatModel:
    """Costruisce il modello di chat in base a settings.llm_provider."""
    settings=settings or get_settings()

    if settings.llm_provider=="gemini":
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            google_api_key=settings.google_api_key,
        )

    if settings.llm_provider=="ollama":
        return ChatOllama(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            base_url=settings.ollama_base_url,
        )

    raise ValueError(f"LLM provider non supportato: {settings.llm_provider}")

def get_embeddings(settings:Settings|None=None)->Embeddings:
    """Costruisce il modello di embedding in base a settings.embedding_provider."""
    settings=settings or get_settings()

    if settings.embedding_provider=="gemini":
        return GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )

    if settings.embedding_provider=="huggingface":
        return HuggingFaceEmbeddings(model_name=settings.embedding_model)
    
    raise ValueError(f"Embedding provider non supportato: {settings.embedding_provider}")