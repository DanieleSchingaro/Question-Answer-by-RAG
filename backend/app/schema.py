#backend/app/schema.py
"""
Modelli Pydantic per richieste e risposte dall'API
"""


from pydantic import BaseModel, Field
from langchain_core.documents import Document

class QueryRequest(BaseModel):
    question:str=Field(
        ...,
        min_length=1,
        description="La domanda da porre sul corpus indicizzato.",
        examples=["Cos'è il Retrieval-Augmented Generation?"],
    )

class SourceDocument(BaseModel):
    content:str=Field(..., description="Estratto del chunk usato come fonte.")
    source:str|None=Field(None, description="Nome del file di origine.")
    page:int|None=Field(None, description="Pagina di origine (solo PDF).")

    @classmethod
    def from_document(cls, doc:Document)->"SourceDocument":
        """Costruisce lo schema a partire da un documento di LangChain."""
        meta=doc.metadata or {}
        return cls(
            content=doc.page_content,
            source=meta.get("source"),
            page=meta.get("page"),
        )
    
class QueryResponse(BaseModel):
    answer:str=Field(
        ..., description="Risposta generata, ancorata al contesto recuperato."
    )
    sources:list[SourceDocument]=Field(
        default_factory=list, description="Documenti usati come contesto."
    )

class IngestResponse(BaseModel):
    documents:int=Field(..., description="Numero di documenti caricati.")
    chunks:int=Field(..., description="Numero di chunk indicizzati.")
    message:str=Field(..., description="Messaggio di esito dell'operazione.")

class HealtResponse(BaseModel):
    status:str=Field("ok", description="Stato del servizio.")
    llm_provider:str=Field(..., description="Provider LLM attivo.")
    llm_model:str=Field(..., description="Modello LLM attivo.")
    embedding_provider:str=Field(..., description="Provider embeddings attivo.")