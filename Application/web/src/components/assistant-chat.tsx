"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type {
  AssistantChatMessage,
  AssistantChatResult,
  ProductSummary,
} from "@/lib/types";

interface ChatEntry extends AssistantChatMessage {
  id: number;
  products?: ProductSummary[];
}

const QUICK_PROMPTS: Record<"customer" | "ops", string[]> = {
  customer: [
    "What are the delivery fees?",
    "How do returns work?",
    "Show me kettles",
    "What are the best selling products in Tanzania?",
  ],
  ops: [
    "How do payouts work?",
    "How do I override a cargo batch?",
    "What is our commission?",
    "How do returns reach the ledger?",
  ],
};

const INTRO: Record<"customer" | "ops", string> = {
  customer: "Hi, I'm Ask Usiri. Ask about products, delivery, returns or payments.",
  ops: "Operations assistant. Ask about payouts, cargo overrides, returns or settings.",
};

const OPS_ROLES = new Set(["ops_admin", "ops_finance", "ops_support", "superadmin"]);
const HIDDEN_PREFIXES = ["/login", "/register", "/pay/"];

export function AssistantWidget() {
  const pathname = usePathname() ?? "";
  const { ready, user } = useAuth();
  const audience: "customer" | "ops" =
    pathname === "/ops" || pathname.startsWith("/ops/") ? "ops" : "customer";

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatEntry[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [model, setModel] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const nextId = useRef(1);

  const hidden = HIDDEN_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  const opsBlocked =
    audience === "ops" && (!ready || !user || !OPS_ROLES.has(user.role));

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  useEffect(() => {
    const node = listRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messages, busy]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  if (hidden || opsBlocked) return null;

  async function send(event: React.FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || busy) return;
    const history: AssistantChatMessage[] = messages
      .slice(-8)
      .map(({ role, content }) => ({ role, content }));
    setMessages((current) => [
      ...current,
      { id: nextId.current++, role: "user", content: text },
    ]);
    setInput("");
    setBusy(true);
    setError("");
    try {
      const result = await api<AssistantChatResult>("/assistant/chat", {
        method: "POST",
        body: { message: text, history, audience },
        auth: audience === "ops",
      });
      setMessages((current) => [
        ...current,
        {
          id: nextId.current++,
          role: "assistant",
          content: result.reply,
          products: result.products,
        },
      ]);
      setNote(result.note);
      setModel(result.model ?? (result.provider === "mock" ? "Demo mode" : result.provider));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function clearChat() {
    setMessages([]);
    setError("");
    setNote("");
    setModel("");
  }

  return (
    <>
      {open ? (
        <section className="assistant-panel" role="dialog" aria-label="Chat assistant">
          <header className="assistant-head">
            <div className="assistant-title">
              <strong>{audience === "ops" ? "Operations assistant" : "Ask Usiri"}</strong>
              <span className="tiny faint">
                {model || (audience === "ops" ? "Internal help" : "Shopping help")}
              </span>
            </div>
            <div className="row" style={{ gap: 4 }}>
              {messages.length > 0 ? (
                <button type="button" className="btn btn-ghost btn-sm" onClick={clearChat}>
                  Clear
                </button>
              ) : null}
              <button
                type="button"
                className="assistant-close"
                onClick={() => setOpen(false)}
                aria-label="Close chat"
              >
                ×
              </button>
            </div>
          </header>

          <div className="assistant-body" ref={listRef} aria-live="polite">
            {messages.length === 0 ? (
              <div className="assistant-intro">
                <p>{INTRO[audience]}</p>
                <div className="assistant-prompts">
                  {QUICK_PROMPTS[audience].map((prompt) => (
                    <button
                      key={prompt}
                      type="button"
                      onClick={() => {
                        setInput(prompt);
                        inputRef.current?.focus();
                      }}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((entry) => (
                <div key={entry.id} className={`assistant-msg ${entry.role}`}>
                  <p>{entry.content}</p>
                  {entry.products && entry.products.length > 0 ? (
                    <div className="assistant-products">
                      {entry.products.map((product) => (
                        <Link
                          key={product.id}
                          href={`/product/${product.slug}`}
                          className="assistant-product"
                          onClick={() => setOpen(false)}
                        >
                          <span>{product.name}</span>
                          <span className="tiny faint">
                            {product.brand ? `${product.brand} · ` : ""}
                            {product.department_name ?? "Catalogue"}
                          </span>
                        </Link>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))
            )}
            {busy ? (
              <div className="assistant-msg assistant">
                <p className="faint">Thinking…</p>
              </div>
            ) : null}
            {error ? <div className="assistant-error">{error}</div> : null}
          </div>

          {note ? <p className="assistant-note">{note}</p> : null}

          <form className="assistant-form" onSubmit={send}>
            <input
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={
                audience === "ops" ? "Ask about a process…" : "Ask about a product or delivery…"
              }
              maxLength={1000}
              aria-label="Message the assistant"
            />
            <button
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={busy || !input.trim()}
            >
              Send
            </button>
          </form>
        </section>
      ) : null}

      <button
        type="button"
        className="assistant-fab"
        onClick={() => setOpen((current) => !current)}
        aria-label={open ? "Close chat assistant" : "Open chat assistant"}
        aria-expanded={open}
      >
        {open ? <span aria-hidden="true">×</span> : <ChatIcon />}
      </button>
    </>
  );
}

function ChatIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 12a8 8 0 0 1-8 8H8l-5 3V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8z" />
      <path d="M8 11h.01M12 11h.01M16 11h.01" />
    </svg>
  );
}
