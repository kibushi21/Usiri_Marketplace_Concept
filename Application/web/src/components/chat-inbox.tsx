"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ChatThread } from "@/components/chat-thread";
import { Alert, Empty, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { fromNow } from "@/lib/format";
import type { ChatConversation } from "@/lib/types";

type DeskFilter = "all" | "supplier" | "logistics";

const FILTERS: { id: DeskFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "supplier", label: "With supplier" },
  { id: "logistics", label: "Logistics desk" },
];

export function ChatInbox({ audience }: { audience: "supplier" | "ops" }) {
  const [items, setItems] = useState<ChatConversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<DeskFilter>("all");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    const data = await api<{ items: ChatConversation[] }>("/chats");
    setItems(data.items);
    setSelectedId((current) => {
      if (current && data.items.some((item) => item.id === current)) return current;
      return data.items[0]?.id ?? null;
    });
  }, []);

  useEffect(() => {
    let active = true;
    load()
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [load]);

  const upsert = useCallback((conversation: ChatConversation) => {
    setItems((current) => {
      const index = current.findIndex((item) => item.id === conversation.id);
      if (index === -1) return [conversation, ...current];
      const next = [...current];
      next[index] = { ...next[index], ...conversation };
      return next.sort((a, b) => b.last_message_at.localeCompare(a.last_message_at));
    });
  }, []);

  const filtered = useMemo(
    () =>
      filter === "all"
        ? items
        : items.filter((item) => item.assigned_party === filter),
    [filter, items],
  );

  const selected = filtered.find((item) => item.id === selectedId) ?? null;

  async function refresh() {
    setRefreshing(true);
    setError("");
    try {
      await load();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setRefreshing(false);
    }
  }

  if (loading) return <Loading label="Opening the conversation list…" />;

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="spread" style={{ gap: 12, flexWrap: "wrap" }}>
        <div className="chip-row">
          {FILTERS.map((entry) => (
            <button
              key={entry.id}
              type="button"
              className={`chip${filter === entry.id ? " active" : ""}`}
              onClick={() => setFilter(entry.id)}
            >
              {entry.label}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="btn btn-ghost btn-sm"
          onClick={refresh}
          disabled={refreshing}
        >
          {refreshing ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {items.length === 0 ? (
        <Empty title="No conversations yet">
          A shared thread opens for every supplier order. Customers, suppliers and the logistics
          desk all write in the same place.
        </Empty>
      ) : (
        <div className="chat-layout">
          <aside className="chat-list" aria-label="Conversations">
            {filtered.length === 0 ? (
              <p className="small faint" style={{ padding: "12px 14px", margin: 0 }}>
                No conversations match this filter.
              </p>
            ) : (
              filtered.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`chat-item${item.id === selectedId ? " active" : ""}`}
                  onClick={() => setSelectedId(item.id)}
                  aria-current={item.id === selectedId ? "true" : undefined}
                >
                  <div className="spread" style={{ gap: 8 }}>
                    <strong>{item.order_code ?? item.code}</strong>
                    <span className="tiny faint">{fromNow(item.last_message_at)}</span>
                  </div>
                  <div className="small faint">
                    {audience === "ops"
                      ? `${item.customer_name} · ${item.supplier_name}`
                      : item.customer_name}
                  </div>
                  <div className="chat-snippet">
                    {item.last_message?.body ?? "No messages yet"}
                  </div>
                  <span
                    className={`badge ${
                      item.assigned_party === "logistics" ? "badge-blue" : "badge-neutral"
                    }`}
                  >
                    {item.assigned_name}
                  </span>
                </button>
              ))
            )}
          </aside>

          <div className="chat-pane">
            {selected ? (
              <>
                {audience === "ops" ? (
                  <div className="chat-context small faint">
                    {selected.customer_name} · {selected.supplier_name}
                    {selected.supplier_order_code ? ` · ${selected.supplier_order_code}` : ""}
                    {selected.shipment
                      ? ` · ${selected.shipment.carrier} ${
                          selected.shipment.tracking_number ?? ""
                        }`
                      : ""}
                  </div>
                ) : null}
                <ChatThread
                  key={selected.id}
                  conversationId={selected.id}
                  onConversation={upsert}
                />
              </>
            ) : (
              <Empty title="Pick a conversation">
                Select an order thread from the list to read and reply.
              </Empty>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
