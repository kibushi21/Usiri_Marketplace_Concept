"use client";

import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";

import { API_URL, api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { date } from "@/lib/format";
import type { ChatConversation, ChatMessage } from "@/lib/types";

type SocketState = "connecting" | "live" | "offline";

const PARTY_LABEL: Record<ChatMessage["author_party"], string> = {
  customer: "Customer",
  supplier: "Supplier",
  logistics: "Logistics desk",
  system: "Usiri",
};

function socketUrl(conversationId: string, token: string): string {
  const url = new URL(API_URL, window.location.origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = `${url.pathname.replace(/\/$/, "")}/chats/${conversationId}/ws`;
  url.search = new URLSearchParams({ token }).toString();
  return url.toString();
}

export function ChatThread({
  conversationId,
  onConversation,
}: {
  conversationId: string;
  onConversation?: (conversation: ChatConversation) => void;
}) {
  const { user, token } = useAuth();
  const [conversation, setConversation] = useState<ChatConversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [socketState, setSocketState] = useState<SocketState>("connecting");
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const bodyRef = useRef<HTMLDivElement>(null);
  const notify = useRef(onConversation);
  notify.current = onConversation;

  const load = useCallback(async () => {
    const data = await api<ChatConversation>(`/chats/${conversationId}`);
    setConversation(data);
    return data;
  }, [conversationId]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api<ChatConversation>(`/chats/${conversationId}`)
      .then((data) => {
        if (active) setConversation(data);
      })
      .catch((cause) => {
        if (active) setError((cause as Error).message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [conversationId]);

  useEffect(() => {
    if (conversation) notify.current?.(conversation);
  }, [conversation]);

  const appendMessage = useCallback((message: ChatMessage) => {
    setConversation((current) => {
      if (!current) return current;
      if (current.messages?.some((item) => item.id === message.id)) return current;
      return {
        ...current,
        messages: [...(current.messages ?? []), message],
        last_message: message,
        last_message_at: message.created_at,
      };
    });
  }, []);

  useEffect(() => {
    if (!token) return;
    let stopped = false;
    let retry: ReturnType<typeof setTimeout> | undefined;
    let ping: ReturnType<typeof setInterval> | undefined;
    let socket: WebSocket | null = null;

    const connect = () => {
      if (stopped) return;
      setSocketState("connecting");
      socket = new WebSocket(socketUrl(conversationId, token));
      socket.onopen = () => {
        if (stopped) return;
        setSocketState("live");
        ping = setInterval(() => {
          if (socket?.readyState === WebSocket.OPEN) socket.send("ping");
        }, 25_000);
        load().catch(() => undefined);
      };
      socket.onmessage = (event) => {
        let payload: {
          type?: string;
          message?: ChatMessage;
          assigned_party?: string;
        };
        try {
          payload = JSON.parse(String(event.data));
        } catch {
          return;
        }
        if (payload.type !== "message" || !payload.message) return;
        appendMessage(payload.message);
        if (payload.assigned_party) load().catch(() => undefined);
      };
      socket.onclose = () => {
        if (ping) clearInterval(ping);
        if (stopped) return;
        setSocketState("offline");
        retry = setTimeout(connect, 2500);
      };
      socket.onerror = () => socket?.close();
    };

    connect();
    return () => {
      stopped = true;
      if (ping) clearInterval(ping);
      if (retry) clearTimeout(retry);
      socket?.close();
    };
  }, [appendMessage, conversationId, load, token]);

  const messageCount = conversation?.messages?.length ?? 0;
  useEffect(() => {
    const node = bodyRef.current;
    if (node) node.scrollTop = node.scrollHeight;
  }, [messageCount, loading]);

  async function submit(event?: FormEvent) {
    event?.preventDefault();
    const body = draft.trim();
    if (!body || sending || !conversation?.can_reply) return;
    setSending(true);
    setError("");
    try {
      const data = await api<{ message: ChatMessage }>(
        `/chats/${conversationId}/messages`,
        { method: "POST", body: { body } },
      );
      appendMessage(data.message);
      setDraft("");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setSending(false);
    }
  }

  async function handOff() {
    const note = window.prompt(
      "Add a short note for the logistics desk (optional). The customer stays in this thread.",
    );
    if (note === null) return;
    setBusy("handoff");
    setError("");
    try {
      const data = await api<{ conversation: ChatConversation }>(
        `/chats/${conversationId}/handoff`,
        { method: "POST", body: { note: note.trim() || null } },
      );
      setConversation(data.conversation);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function assign(party: "logistics" | "supplier") {
    const prompt =
      party === "logistics"
        ? "Take over this conversation from the supplier?"
        : "Return this conversation to the supplier?";
    if (!window.confirm(prompt)) return;
    setBusy(party);
    setError("");
    try {
      const data = await api<{ conversation: ChatConversation }>(
        `/chats/${conversationId}/assign`,
        { method: "POST", body: { party } },
      );
      setConversation(data.conversation);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  const messages = conversation?.messages ?? [];
  const socketLabel =
    socketState === "live"
      ? "Live"
      : socketState === "connecting"
        ? "Connecting"
        : "Reconnecting";

  return (
    <section className="chat-thread" aria-label="Order conversation">
      <header className="chat-head">
        <div>
          <div className="chat-title">
            Order chat
            {conversation?.order_code ? ` · ${conversation.order_code}` : ""}
          </div>
          <div className="small faint">
            {conversation?.supplier_name ?? "Supplier"}
            {conversation?.customer_name ? ` · ${conversation.customer_name}` : ""}
            {conversation?.shipment
              ? ` · ${conversation.shipment.carrier}${
                  conversation.shipment.tracking_number
                    ? ` ${conversation.shipment.tracking_number}`
                    : ""
                }`
              : ""}
          </div>
        </div>
        <div className="chat-head-side">
          <span className={`chat-live ${socketState}`}>
            <span className="chat-live-dot" />
            {socketLabel}
          </span>
          {conversation ? (
            <span
              className={`badge ${
                conversation.assigned_party === "logistics" ? "badge-blue" : "badge-neutral"
              }`}
            >
              {conversation.assigned_name}
            </span>
          ) : null}
        </div>
      </header>

      <div className="chat-body" ref={bodyRef} aria-live="polite">
        {loading ? <div className="chat-note">Loading the conversation…</div> : null}
        {!loading && messages.length === 0 ? (
          <div className="chat-note">No messages yet. Say hello.</div>
        ) : null}
        {messages.map((message) => {
          if (message.kind !== "text") {
            return (
              <div key={message.id} className="chat-system">
                <span>{message.body}</span>
                <time>{date(message.created_at)}</time>
              </div>
            );
          }
          const own = message.author_id !== null && message.author_id === user?.id;
          return (
            <div key={message.id} className={`chat-line${own ? " own" : ""}`}>
              <div className="chat-meta">
                <strong>{message.author_name}</strong>
                <span>{PARTY_LABEL[message.author_party]}</span>
                <time>{date(message.created_at)}</time>
              </div>
              <div className="chat-bubble">{message.body}</div>
            </div>
          );
        })}
      </div>

      {error ? <div className="chat-error">{error}</div> : null}

      {conversation?.can_handoff ? (
        <div className="chat-actions">
          <span className="small faint">
            The items have left the supplier. Delivery questions can move to the Usiri
            logistics desk.
          </span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handOff}
            disabled={busy !== ""}
          >
            {busy === "handoff" ? "Handing over…" : "Hand to logistics"}
          </button>
        </div>
      ) : null}

      {conversation && (conversation.can_take_over || conversation.can_return) ? (
        <div className="chat-actions">
          <span className="small faint">
            {conversation.can_take_over
              ? "The supplier currently owns this thread."
              : "Your desk owns this thread."}
          </span>
          {conversation.can_take_over ? (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => assign("logistics")}
              disabled={busy !== ""}
            >
              {busy === "logistics" ? "Taking over…" : "Take over"}
            </button>
          ) : null}
          {conversation.can_return ? (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => assign("supplier")}
              disabled={busy !== ""}
            >
              {busy === "supplier" ? "Returning…" : "Return to supplier"}
            </button>
          ) : null}
        </div>
      ) : null}

      {conversation?.can_reply ? (
        <form className="chat-compose" onSubmit={submit}>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) void submit(event);
            }}
            placeholder="Write a message… (Enter to send, Shift+Enter for a new line)"
            maxLength={2000}
            rows={2}
            aria-label="Message"
          />
          <button
            type="submit"
            className="btn btn-primary btn-sm"
            disabled={sending || !draft.trim()}
          >
            {sending ? "Sending…" : "Send"}
          </button>
        </form>
      ) : conversation ? (
        <div className="chat-locked small faint">
          {conversation.assigned_party === "logistics"
            ? "The Usiri logistics desk is handling this conversation."
            : "The supplier is handling this conversation."}
        </div>
      ) : null}
    </section>
  );
}
