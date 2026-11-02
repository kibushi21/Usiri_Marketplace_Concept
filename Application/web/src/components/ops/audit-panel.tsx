"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

import { Alert, Badge, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { date, fromNow, titleCase } from "@/lib/format";
import type { AuditEntry } from "@/lib/types";

export function OpsAuditPanel() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [entityTypes, setEntityTypes] = useState<string[]>([]);
  const [action, setAction] = useState("");
  const [entityType, setEntityType] = useState("");
  const [query, setQuery] = useState({ action: "", entityType: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ limit: "200" });
      if (query.action) params.set("action", query.action);
      if (query.entityType) params.set("entity_type", query.entityType);
      const data = await api<{ items: AuditEntry[] }>(`/ops/audit?${params.toString()}`);
      setEntries(data.items);
      setEntityTypes((current) => {
        const next = new Set(current);
        for (const entry of data.items) next.add(entry.entity_type);
        return [...next].sort();
      });
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, [query]);

  useEffect(() => {
    void load();
  }, [load]);

  function submit(event: FormEvent) {
    event.preventDefault();
    setQuery({ action: action.trim(), entityType });
  }

  return (
    <div className="stack">
      <form className="inline-form" onSubmit={submit}>
        <label className="field" style={{ flex: 1 }}>
          <span>Action contains</span>
          <input
            value={action}
            onChange={(event) => setAction(event.target.value)}
            placeholder="e.g. payout, config, return"
          />
        </label>
        <label className="field">
          <span>Entity</span>
          <select value={entityType} onChange={(event) => setEntityType(event.target.value)}>
            <option value="">All entities</option>
            {entityTypes.map((type) => (
              <option key={type} value={type}>
                {titleCase(type)}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="btn btn-primary">
          Filter
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => {
            setAction("");
            setEntityType("");
            setQuery({ action: "", entityType: "" });
          }}
        >
          Clear
        </button>
      </form>

      {error ? <Alert kind="error">{error}</Alert> : null}

      {loading ? (
        <Loading label="Loading the audit trail…" />
      ) : entries.length === 0 ? (
        <p className="muted">No audit entries match this filter.</p>
      ) : (
        <section className="card">
          <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Change</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.id}>
                    <td className="small">
                      <div>{date(entry.created_at)}</div>
                      <div className="faint">{fromNow(entry.created_at)}</div>
                    </td>
                    <td className="small">
                      <div>{entry.actor}</div>
                      <div className="faint">
                        {(entry.actor_role ?? "system").replaceAll("_", " ")}
                      </div>
                    </td>
                    <td>
                      <Badge tone="brand">{entry.action}</Badge>
                    </td>
                    <td className="small">
                      <div>{titleCase(entry.entity_type)}</div>
                      <div className="faint" style={{ fontFamily: "ui-monospace, monospace" }}>
                        {entry.entity_id ? entry.entity_id.slice(0, 8) : "—"}
                      </div>
                    </td>
                    <td style={{ maxWidth: 360 }}>
                      {entry.before || entry.after ? (
                        <details>
                          <summary className="small" style={{ cursor: "pointer" }}>
                            Show before and after
                          </summary>
                          <pre className="small" style={{ whiteSpace: "pre-wrap", marginTop: 6 }}>
                            {JSON.stringify({ before: entry.before, after: entry.after }, null, 2)}
                          </pre>
                        </details>
                      ) : (
                        <span className="small faint">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
      <p className="small faint">
        The audit trail is append-only. It records who changed what, including configuration and
        payout decisions, with the values before and after the change.
      </p>
    </div>
  );
}
