"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { date, fromNow, titleCase } from "@/lib/format";
import type { Ticket } from "@/lib/types";

const FILTERS = ["", "open", "in_progress", "resolved", "closed"];
const STATUSES = ["open", "in_progress", "resolved", "closed"];
const PRIORITIES = ["low", "normal", "high", "urgent"];

export function OpsTicketsPanel() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [filter, setFilter] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<Ticket | null>(null);
  const [threadLoading, setThreadLoading] = useState(false);
  const [busy, setBusy] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [reply, setReply] = useState("");
  const [internal, setInternal] = useState(false);

  const load = useCallback(async () => {
    setError("");
    try {
      const suffix = filter ? `?status=${filter}` : "";
      const data = await api<{ items: Ticket[] }>(`/ops/tickets${suffix}`);
      setTickets(data.items);
      setSelectedId((current) => {
        if (current && data.items.some((ticket) => ticket.id === current)) return current;
        return data.items[0]?.id ?? null;
      });
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let active = true;
    setThreadLoading(true);
    api<Ticket>(`/support/tickets/${selectedId}`)
      .then((data) => {
        if (active) setDetail(data);
      })
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setThreadLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedId]);

  async function act(label: string, request: () => Promise<unknown>, message: string) {
    setBusy(label);
    setError("");
    setNotice("");
    try {
      await request();
      await load();
      if (selectedId) {
        setDetail(await api<Ticket>(`/support/tickets/${selectedId}`));
      }
      setNotice(message);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  const current = tickets.find((ticket) => ticket.id === selectedId) ?? detail;

  async function send() {
    if (!detail || !reply.trim()) return;
    setBusy("reply");
    setError("");
    try {
      await api(`/support/tickets/${detail.id}/messages`, {
        method: "POST",
        body: { body: reply.trim(), internal },
      });
      setReply("");
      setDetail(await api<Ticket>(`/support/tickets/${detail.id}`));
      await load();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="stack">
      <div className="chip-row">
        {FILTERS.map((value) => (
          <button
            key={value || "all"}
            type="button"
            className={`chip${filter === value ? " active" : ""}`}
            onClick={() => setFilter(value)}
          >
            {value ? titleCase(value) : "All"}
          </button>
        ))}
      </div>

      {error ? <Alert kind="error">{error}</Alert> : null}
      {notice ? <Alert kind="success">{notice}</Alert> : null}

      {loading ? (
        <Loading label="Loading support tickets…" />
      ) : tickets.length === 0 ? (
        <p className="muted">No tickets in this state.</p>
      ) : (
        <div className="split">
          <section className="card" style={{ alignSelf: "start" }}>
            <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Ticket</th>
                    <th>Status</th>
                    <th>Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((ticket) => (
                    <tr
                      key={ticket.id}
                      onClick={() => setSelectedId(ticket.id)}
                      style={{
                        cursor: "pointer",
                        background: ticket.id === selectedId ? "var(--paper-deep)" : undefined,
                      }}
                    >
                      <td>
                        <div style={{ fontWeight: 600 }}>{ticket.subject}</div>
                        <div className="small faint">
                          {ticket.code} · {ticket.customer_name ?? "Customer"}
                          {ticket.order_code ? ` · ${ticket.order_code}` : ""}
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={ticket.status} />
                      </td>
                      <td>
                        <span className="small">{titleCase(ticket.priority)}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card card-pad">
            {!current ? (
              <p className="muted small">Select a ticket to read the conversation.</p>
            ) : (
              <div className="stack">
                <div className="spread" style={{ alignItems: "flex-start" }}>
                  <div>
                    <h2 style={{ fontSize: "1.05rem" }}>{current.subject}</h2>
                    <p className="small faint" style={{ marginTop: 4 }}>
                      {current.code} · {titleCase(current.category)} ·{" "}
                      {current.customer_name ?? "Customer"} · opened {date(current.created_at)}
                      {current.order_code ? ` · ${current.order_code}` : ""}
                    </p>
                  </div>
                  <StatusBadge status={current.status} />
                </div>

                <div className="inline-form">
                  <label className="field">
                    <span>Status</span>
                    <select
                      value={STATUSES.includes(current.status) ? current.status : "open"}
                      disabled={busy !== ""}
                      onChange={(event) =>
                        act(
                          "status",
                          () =>
                            api(`/ops/tickets/${current.id}`, {
                              method: "PATCH",
                              body: { status: event.target.value },
                            }),
                          "Ticket status updated.",
                        )
                      }
                    >
                      {STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {titleCase(status)}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="field">
                    <span>Priority</span>
                    <select
                      value={PRIORITIES.includes(current.priority) ? current.priority : "normal"}
                      disabled={busy !== ""}
                      onChange={(event) =>
                        act(
                          "priority",
                          () =>
                            api(`/ops/tickets/${current.id}`, {
                              method: "PATCH",
                              body: { priority: event.target.value },
                            }),
                          "Priority updated.",
                        )
                      }
                    >
                      {PRIORITIES.map((priority) => (
                        <option key={priority} value={priority}>
                          {titleCase(priority)}
                        </option>
                      ))}
                    </select>
                  </label>
                  {current.assigned_to !== user?.id ? (
                    <button
                      type="button"
                      className="btn btn-secondary"
                      disabled={busy !== ""}
                      onClick={() =>
                        act(
                          "assign",
                          () =>
                            api(`/ops/tickets/${current.id}`, {
                              method: "PATCH",
                              body: { assigned_to: user?.id ?? "" },
                            }),
                          "You are now assigned to this ticket.",
                        )
                      }
                    >
                      Assign to me
                    </button>
                  ) : (
                    <span className="small faint" style={{ alignSelf: "center" }}>
                      Assigned to you
                    </span>
                  )}
                </div>

                {threadLoading || !detail || detail.id !== current.id ? (
                  <Loading label="Loading the conversation…" />
                ) : (
                  <>
                    <div className="stack-sm" style={{ maxHeight: 380, overflowY: "auto" }}>
                      {(detail.messages ?? []).length === 0 ? (
                        <p className="muted small">No messages yet.</p>
                      ) : (
                        (detail.messages ?? []).map((message) => {
                          const author =
                            message.author_id === current.customer_id
                              ? current.customer_name ?? "Customer"
                              : message.author_id === user?.id
                                ? "You"
                                : "Support team";
                          return (
                            <article
                              key={message.id}
                              className="card card-pad"
                              style={{
                                background: message.internal ? "#fdf3e6" : undefined,
                                borderColor: message.internal ? "#e6c9a3" : undefined,
                              }}
                            >
                              <div className="spread small faint">
                                <span>
                                  <strong style={{ color: "var(--ink)" }}>{author}</strong>
                                  {message.internal ? " · internal note" : ""}
                                </span>
                                <span>{fromNow(message.created_at)}</span>
                              </div>
                              <p style={{ marginTop: 6, whiteSpace: "pre-wrap" }}>{message.body}</p>
                            </article>
                          );
                        })
                      )}
                    </div>

                    <div className="inline-form" style={{ alignItems: "flex-end" }}>
                      <label className="field" style={{ flex: 1 }}>
                        <span>Reply</span>
                        <textarea
                          rows={3}
                          value={reply}
                          onChange={(event) => setReply(event.target.value)}
                          placeholder="Write a response to the customer"
                        />
                      </label>
                      <label className="row small" style={{ gap: 6, alignSelf: "center" }}>
                        <input
                          type="checkbox"
                          checked={internal}
                          onChange={(event) => setInternal(event.target.checked)}
                        />
                        Internal note
                      </label>
                      <button
                        type="button"
                        className="btn btn-primary"
                        disabled={busy !== "" || !reply.trim()}
                        onClick={send}
                      >
                        {busy === "reply" ? "Sending…" : "Send"}
                      </button>
                    </div>
                    <p className="small faint">
                      Internal notes stay visible to staff only and are hidden from the customer.
                    </p>
                  </>
                )}
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
