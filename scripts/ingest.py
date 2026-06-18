#scripts/ingest.py
"""
CLI per indicizzare documenti nel vector store.
Uso: pytho scripts/ingest.py <percorso>

<percorso> è un file singolo o una cartella contenente file .txt/.md/.pdf.
Utile ad indicizzare interi corpus senza passare dall'endpoint /ingest.
"""

import argparse
import sys
from pathlib import Path

#Rende importabile il package 'app' quando lo script viene lanciato direttamente
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.ingest import ingest  # noqa: E402

def main()->None:
    parser=argparse.ArgumentParser(
        description="Indicizza documenti (.txt/.md/.pdf) nel vector store RAG."
    )
    parser.add_argument(
        "path",
        help="File o cartella da indicizzare.",
    )
    args=parser.parse_args()

    target=Path(args.path)
    if not target.exists():
        print(f"Errore: percorso non trovato -> {target}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Indicizzazione di: {target} ...")
    result=ingest(target)

    if result["chunks"]==0:
        print("Nessun contenuto indicizzato (file vuoti o non supportati).")
        sys.exit(1)
    
    print(
        f"Fatto: indicizzati {result['chunks']} chunk "
        f"da {result['documents']} documento/i."
    )

if __name__=="__main__":
    main()