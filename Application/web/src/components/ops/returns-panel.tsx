"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money, titleCase } from "@/lib/format";
import type { ReturnRecord } from "@/lib/types";

const FILTERS = ["", "requested", "approved", "refunded", "rejected"];

export function OpsReturnsPanel() {
  const [returns, setReturns] = useState<ReturnRecord[]>([]);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const suffix = filter ? `?status=${filter}` : "";
      const data = await api<{ items: ReturnRecord[] }>(`/ops/returns${suffix}`);
      setReturns(data.items);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    void load();
  }, [load]);

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
        <Loading label="Loading returns…" />
      ) : returns.length === 0 ? (
        <p className="muted">No returns in this state.</p>
      ) : (
        <div className="stack-sm">
          {returns.map((entry) => (
            <ReturnCard
              key={entry.id}
              entry={entry}
              onChanged={async (message) => {
                setNotice(message);
                await load();
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ReturnCard({
  entry,
  onChanged,
}: {
  entry: ReturnRecord;
  onChanged: (message: string) => Promise<void>;
}) {
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  async function decide(approve: boolean) {
    setBusy(approve ? "approve" : "reject");
    setError("");
    try {
      await api(`/ops/returns/${entry.id}/decide`, {
        method: "POST",
        body: { approve, note: note || null },
      });
      await onChanged(approve ? `${entry.code} approved.` : `${entry.code} rejected.`);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function receive() {
    setBusy("receive");
    setError("");
    try {
      const result = await api<{ refund_amount: number }>(`/ops/returns/${entry.id}/receive`, {
        method: "POST",
      });
      await onChanged(`${entry.code} refunded (${money(result.refund_amount)}).`);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  return (
    <article className="card card-pad">
      <div className="spread" style={{ alignItems: "flex-start" }}>
        <div>
          <div className="row" style={{ gap: 10 }}>
            <strong>{entry.code}</strong>
            <StatusBadge status={entry.status} />
          </div>
          <div className="small muted" style={{ marginTop: 5 }}>
            {entry.order_code ?? entry.order_id.slice(0, 8)} · {entry.item?.product_name ?? "Item"} ×{" "}
            {entry.qty} · {titleCase(entry.reason)}
          </div>
          <div className="small faint" style={{ marginTop: 3 }}>
            Requested {date(entry.requested_at)} · unit {money(entry.item?.unit_price ?? 0)}
            {entry.refund_amount ? ` · refunded ${money(entry.refund_amount)}` : ""}
          </div>
          {entry.details ? <p className="small muted" style={{ marginTop: 6 }}>“{entry.details}”</p> : null}
          {entry.decision_note ? (
            <p className="small faint" style={{ marginTop: 4 }}>
              Note: {entry.decision_note}
            </p>
          ) : null}
        </div>
        <div className="right small faint">{entry.status === "refunded" ? "Closed" : ""}</div>
      </div>

      {error ? <div style={{ marginTop: 10 }}><Alert kind="error">{error}</Alert></div> : null}

      {entry.status === "requested" ? (
        <div style={{ marginTop: 12 }}>
          <div className="inline-form">
            <label className="field">
              <span>Decision note</span>
              <input value={note} onChange={(event) => setNote(event.target.value)} placeholder="Optional" />
            </label>
            <button type="button" className="btn btn-primary" disabled={busy !== ""} onClick={() => decide(true)}>
              {busy === "approve" ? "Approving…" : "Approve return"}
            </button>
            <button type="button" className="btn btn-danger" disabled={busy !== ""} onClick={() => decide(false)}>
              {busy === "reject" ? "Rejecting…" : "Reject"}
            </button>
          </div>
        </div>
      ) : null}

      {entry.status === "approved" ? (
        <div className="btn-row" style={{ marginTop: 12 }}>
          <button type="button" className="btn btn-primary" disabled={busy !== ""} onClick={receive}>
            {busy === "receive" ? "Refunding…" : `Receive and refund ${money(entry.qty * (entry.item?.unit_price ?? 0))}`}
          </button>
        </div>
      ) : null}
    </article>
  );
}
