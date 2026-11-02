"use client";

import { useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { Alert, Empty, Loading, PageHead, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, titleCase } from "@/lib/format";
import type { Order, Ticket } from "@/lib/types";

const CATEGORIES = [
  { id: "order", label: "Order" },
  { id: "delivery", label: "Delivery" },
  { id: "payment", label: "Payment" },
  { id: "return", label: "Return" },
  { id: "product", label: "Product" },
  { id: "general", label: "Something else" },
];

export default function SupportPage() {
  return (
    <RequireAuth roles={["customer"]}>
      <SupportView />
    </RequireAuth>
  );
}

function SupportView() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [selected, setSelected] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState("");

  const [subject, setSubject] = useState("");
  const [category, setCategory] = useState("general");
  const [orderId, setOrderId] = useState("");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");

  async function loadTickets() {
    const data = await api<{ items: Ticket[] }>("/support/tickets");
    setTickets(data.items);
    return data.items;
  }

  useEffect(() => {
    let active = true;
    Promise.all([loadTickets(), api<{ items: Order[] }>("/orders")])
      .then(([ticketList, orderList]) => {
        if (!active) return;
        setTickets(ticketList);
        setOrders(orderList.items);
      })
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function openTicket(ticketId: string) {
    setBusy("open");
    setError("");
    try {
      const ticket = await api<Ticket>(`/support/tickets/${ticketId}`);
      setSelected(ticket);
      setReply("");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function createTicket(event: React.FormEvent) {
    event.preventDefault();
    setBusy("create");
    setError("");
    setNotice("");
    try {
      const ticket = await api<Ticket>("/support/tickets", {
        method: "POST",
        body: {
          subject: subject.trim(),
          category,
          order_id: orderId || null,
          message: message.trim(),
        },
      });
      setSubject("");
      setMessage("");
      setOrderId("");
      setCategory("general");
      await loadTickets();
      setNotice(`Ticket ${ticket.code} created. Support will reply here.`);
      await openTicket(ticket.id);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function sendReply(event: React.FormEvent) {
    event.preventDefault();
    if (!selected || !reply.trim()) return;
    setBusy("reply");
    setError("");
    try {
      await api(`/support/tickets/${selected.id}/messages`, {
        method: "POST",
        body: { body: reply.trim(), internal: false },
      });
      setReply("");
      await openTicket(selected.id);
      await loadTickets();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (loading) return <Loading label="Opening support…" />;

  return (
    <div className="container portal-body">
      <PageHead
        title="Support"
        description="Ask about an order, delivery, payment or return. Replies stay on the ticket so there is a record."
      />

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}
      {notice ? <div style={{ marginBottom: 16 }}><Alert kind="success">{notice}</Alert></div> : null}

      <div className="split">
        <div className="stack">
          <section className="card card-pad">
            <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>Your tickets</h2>
            {tickets.length === 0 ? (
              <p className="muted small">No tickets yet. Use the form to open one.</p>
            ) : (
              <div className="stack-sm">
                {tickets.map((ticket) => (
                  <button
                    key={ticket.id}
                    type="button"
                    className="row-card"
                    style={{
                      textAlign: "left",
                      cursor: "pointer",
                      borderColor: selected?.id === ticket.id ? "var(--brand)" : undefined,
                      background: selected?.id === ticket.id ? "var(--brand-soft)" : undefined,
                    }}
                    onClick={() => openTicket(ticket.id)}
                  >
                    <div className="spread" style={{ alignItems: "flex-start" }}>
                      <div>
                        <strong style={{ fontSize: ".93rem" }}>{ticket.subject}</strong>
                        <div className="small faint">
                          {ticket.code} · {titleCase(ticket.category)} · {date(ticket.created_at)}
                        </div>
                      </div>
                      <StatusBadge status={ticket.status} />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </section>

          {selected ? (
            <section className="card card-pad">
              <div className="spread" style={{ marginBottom: 12 }}>
                <div>
                  <h2 style={{ fontSize: "1.05rem" }}>{selected.subject}</h2>
                  <div className="small faint">
                    {selected.code} · opened {date(selected.created_at)}
                  </div>
                </div>
                <StatusBadge status={selected.status} />
              </div>

              <div className="stack-sm">
                {(selected.messages ?? []).map((entry) => (
                  <div key={entry.id} className="panel" style={{ background: "var(--surface-2)" }}>
                    <div className="spread" style={{ marginBottom: 4 }}>
                      <span className="tiny faint">
                        {entry.author_id === selected.customer_id ? "You" : "Usiri support"}
                      </span>
                      <span className="tiny faint">{date(entry.created_at)}</span>
                    </div>
                    <p className="small" style={{ whiteSpace: "pre-line" }}>
                      {entry.body}
                    </p>
                  </div>
                ))}
              </div>

              {selected.status === "closed" ? (
                <p className="small muted" style={{ marginTop: 14 }}>
                  This ticket is closed. Start a new one if you need anything else.
                </p>
              ) : (
                <form className="stack-sm" style={{ marginTop: 16 }} onSubmit={sendReply}>
                  <textarea
                    value={reply}
                    onChange={(event) => setReply(event.target.value)}
                    placeholder="Add a reply"
                    required
                  />
                  <button type="submit" className="btn btn-primary" disabled={busy === "reply"}>
                    {busy === "reply" ? "Sending…" : "Send reply"}
                  </button>
                </form>
              )}
            </section>
          ) : null}
        </div>

        <aside className="card card-pad" style={{ position: "sticky", top: 88 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 4 }}>Open a ticket</h2>
          <p className="small faint" style={{ marginBottom: 16 }}>
            Include the order code if it relates to a purchase.
          </p>
          <form className="stack" onSubmit={createTicket}>
            <label className="field">
              <span>Subject</span>
              <input
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                minLength={3}
                maxLength={200}
                required
              />
            </label>
            <label className="field">
              <span>Topic</span>
              <select value={category} onChange={(event) => setCategory(event.target.value)}>
                {CATEGORIES.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Order (optional)</span>
              <select value={orderId} onChange={(event) => setOrderId(event.target.value)}>
                <option value="">Not about a specific order</option>
                {orders.map((order) => (
                  <option key={order.id} value={order.id}>
                    {order.code} · {titleCase(order.stage)}
                  </option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Message</span>
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                minLength={3}
                required
              />
            </label>
            <button type="submit" className="btn btn-primary btn-block" disabled={busy === "create"}>
              {busy === "create" ? "Sending…" : "Create ticket"}
            </button>
          </form>
          {tickets.length === 0 ? (
            <div style={{ marginTop: 18 }}>
              <Empty title="No history yet">Tickets you open will be listed on the left.</Empty>
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
