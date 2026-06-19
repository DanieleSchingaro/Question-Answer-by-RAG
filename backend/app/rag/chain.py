#backend/app/rag/chain.py
"""
Catena RAG costruita in LCEL (LangChain Expression Language)
Flusso:
    {"question":str}
        -> retriever Chroma
        -> prompt (contesto + domanda)
        -> LLM
        -> {"answer":str, "sources":list[Documents]}
"""

from functools import lru_cache
from operator import itemgetter
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from app.config import Settings, get_settings
from app.rag.providers import get_llm
from app.rag.vectorstore import get_vectorstore

SYSTEM_PROMPT=(
    "Sei un assistente che risponde a domande basandoti ESCLUSIVAMENTE sul "
    "CONTESTO fornito qui sotto. Se la risposta non e' presente nel contesto, "
    "dillo chiaramente invece di inventare. Rispondi nella stessa lingua della "
    "domanda, in modo conciso e accurato.\n\n"
    "CONTESTO:\n{context}"
)

PROMPT=ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)

def format_docs(docs:list[Document])->str:
    """Concatena il contenuto dei documenti recuperati in un'unica stringa"""
    return "\n\n---\n\n".join(d.page_content for d in docs)

def build_rag_chain(settings:Settings|None=None)->Runnable:
    """
    Costruisce la catena RAG.
    Input: {"question":str}
    Output: {"answer":str, "sources":list[Document]}
    """
    settings=settings or get_settings()
    retriever=get_vectorstore(settings).as_retriever(
        search_kwargs={"k":settings.retrieval_k}
    )
    llm=get_llm(settings)

    #Genera la risposta a partire da {question, docs}: formatta il contesto,
    #riempie il prompt, interroga l'LLM ed estrae la stringa.
    generate_answer=(
        RunnablePassthrough.assign(context=lambda x:format_docs(x["docs"]))
        |PROMPT
        |llm
        |StrOutputParser()
    )

    #1) dalla domanda recupera i docs mantenendo la domanda originale
    #2) in parallelo produce la risposta e conserva le fonti
    return RunnableParallel(
        question=itemgetter("question"),
        docs=itemgetter("question")|retriever,
    )|RunnableParallel(
        answer=generate_answer,
        sources=itemgetter("docs"),
    )

@lru_cache
def get_rag_chain()->Runnable:
    """
    Catena con impostazioni di default, costruita una sola volta e riusata.
    Il Retriever interroga Chroma a ogni chiamata,
    vedendo quindi anche i documenti indicizzati dopo la creazione.
    """
    return build_rag_chain()

def answer_question(question:str)->dict:
    """Helper sincrono: pone domanda e restituisce risposta + fonti."""
    return get_rag_chain().invoke({"question":question})