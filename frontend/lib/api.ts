//frontend/lib/api.ts

//Client API tipizzato verso il backend FastAPI

const API_URL=process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface SourceDocument{
    content:string;
    source:string|null;
    page:number|null;
}

export interface QueryResponse{
    answer:string;
    sources:SourceDocument[];
}

export interface IngestResponse{
    documents:number;
    chunks:number;
    message:string;
}

export interface Health{
    status:string;
    llm_provider:string;
    llm_model:string;
    embedding_provider:string;
}

//Estrae il messaggio di errore di FastAPI o lancia un HTTP generico
async function handle<T>(res:Response):Promise<T>{
    if (!res.ok){
        let detail=`HTTP ${res.status}`;
        try{
            const data=await res.json();
            if (data?.detail){
                detail=
                    typeof data.detail==="string"
                        ? data.detail
                        : JSON.stringify(data.detail);
            }
        } catch {
            //corpo non-JSON --> messaggio HTTP generico
        }
        throw new Error(detail);
    }
    return res.json() as Promise<T>;
}

export async function getHealth():Promise<Health>{
    const res=await fetch(`${API_URL}/health`);
    return handle<Health>(res);
}

export async function query(question:string):Promise<QueryResponse>{
    const res=await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question}),
    });
    return handle<QueryResponse>(res);
}

export async function ingest(files:File[]):Promise<IngestResponse>{
    const form=new FormData();
    for (const file of files) form.append("files", file);
    const res=await fetch(`${API_URL}/ingest`, {
        method: "POST",
        body: form,
    });
    return handle<IngestResponse>(res);
}