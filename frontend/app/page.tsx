//frontend/app/page.tsx

"use client";

import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import {
  getHealth,
  query,
  ingest,
  type QueryResponse,
  type Health,
  type SourceDocument,
} from "@/lib/api";

const EXAMPLES=[
  "What is Retrieval-Augmented Generation?",
  "Why does RAG reduce hallucinations?",
];

export default function Home() {
  const [question, setQuestion]=useState("");
  const [result, setResult]=useState<QueryResponse | null>(null);
  const [loading, setLoading]=useState(false);
  const [error, setError]=useState<string|null>(null);

  const [health, setHealth]=useState<Health|null>(null);
  const [healthError, setHealthError]=useState(false);

  const [ingesting, setIngesting]=useState(false);
  const [ingestMsg, setIngestMsg]=useState<string|null>(null);
  const fileRef=useRef<HTMLInputElement>(null);

  useEffect(()=>{
    getHealth()
      .then((h)=>{
        setHealth(h);
        setHealthError(false);
      })
      .catch(()=>setHealthError(true));
  }, []);

  async function handleAsk() {
    const q=question.trim();
    if (!q||loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await query(q));
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Something went wrong. Is the backend running on port 8000?"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest(files:FileList|null) {
    if (!files||files.length===0) return;
    setIngesting(true);
    setIngestMsg(null);
    setError(null);
    try {
      const res=await ingest(Array.from(files));
      setIngestMsg(res.message);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Couldn't index the selected files."
      );
    } finally{
      setIngesting(false);
      if (fileRef.current) fileRef.current.value="";
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key==="Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <div className="mx-auto max-w-2xl px-5 py-10 sm:py-16">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="inline-block h-5 w-5 rounded-md bg-indigo-600" />
            <span className="font-mono text-sm font-semibold tracking-tight">
              rag<span className="text-indigo-600">·</span>qa
            </span>
          </div>
          <StatusPill health={health} error={healthError} />
        </header>

        {/* Hero */}
        <section className="mt-12 sm:mt-16">
          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight">
            Ask your documents.
          </h1>
          <p className="mt-2 text-slate-500">
            Answers grounded in your sources — never made up.
          </p>
        </section>

        {/* Ask box */}
        <section className="mt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition focus-within:border-indigo-300 focus-within:ring-2 focus-within:ring-indigo-100">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={onKeyDown}
              rows={3}
              placeholder="Ask anything about your indexed documents…"
              className="block w-full resize-none bg-transparent px-3 py-2 text-slate-900 placeholder:text-slate-400 focus:outline-none"
            />
            <div className="flex items-center justify-between gap-3 px-2 pb-1">
              <button
                onClick={() => fileRef.current?.click()}
                disabled={ingesting}
                className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-slate-500 transition hover:text-slate-900 disabled:opacity-50"
              >
                {ingesting ? <Spinner /> : <PaperclipIcon />}
                {ingesting ? "Indexing…" : "Add documents"}
              </button>
              <button
                onClick={handleAsk}
                disabled={loading||!question.trim()}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {loading ? <Spinner /> : null}
                {loading ? "Thinking…" : "Ask"}
              </button>
            </div>
          </div>

          <input
            ref={fileRef}
            type="file"
            accept=".txt,.md,.pdf"
            multiple
            className="hidden"
            onChange={(e) => handleIngest(e.target.files)}
          />

          {ingestMsg ? (
            <p className="mt-2 px-1 text-sm text-emerald-600">{ingestMsg}</p>
          ) : null}

          {!result && !loading ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setQuestion(ex)}
                  className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                >
                  {ex}
                </button>
              ))}
            </div>
          ) : null}
        </section>

        {/* Error */}
        {error ? (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {/* Result */}
        {result ? (
          <section className="mt-8 space-y-6">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
              <p className="font-mono text-xs uppercase tracking-widest text-slate-400">
                Answer
              </p>
              <p className="mt-3 whitespace-pre-wrap leading-relaxed text-slate-800">
                {result.answer}
              </p>
            </div>

            {result.sources.length > 0 ? (
              <div>
                <p className="font-mono text-xs uppercase tracking-widest text-slate-400">
                  Sources · {result.sources.length}
                </p>
                <div className="mt-3 space-y-3">
                  {result.sources.map((s, i) => (
                    <SourceCard key={i} index={i} source={s} />
                  ))}
                </div>
              </div>
            ) : null}
          </section>
        ) : null}
      </div>
    </div>
  );
}

function StatusPill({ health, error }: { health: Health | null; error: boolean }) {
  const online=!!health && !error;
  const dot=error ? "bg-red-500" : online ? "bg-emerald-500" : "bg-slate-300";
  const label=error ? "API offline" : online ? health!.llm_model : "connecting…";
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5">
      <span className={`h-2 w-2 rounded-full ${dot}`} />
      <span className="font-mono text-xs text-slate-500">{label}</span>
    </div>
  );
}

function SourceCard({ index, source }: { index: number; source: SourceDocument }) {
  const rank=String(index + 1).padStart(2, "0");
  return (
    <div className="rounded-r-xl border-l-2 border-amber-400 bg-amber-50/60 px-4 py-3">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 font-mono text-xs text-amber-500/80">{rank}</span>
        <div className="min-w-0 flex-1">
          <p className="line-clamp-4 font-mono text-sm leading-relaxed text-slate-700">
            {source.content}
          </p>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="truncate font-mono font-medium text-slate-600">
              {source.source ?? "unknown"}
            </span>
            {source.page != null ? (
              <span className="rounded bg-amber-200/70 px-1.5 py-0.5 font-mono text-amber-900">
                p. {source.page}
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

function PaperclipIcon() {
  return (
    <svg
      className="h-4 w-4"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
    </svg>
  );
}