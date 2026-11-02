"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Badge, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { percent, titleCase } from "@/lib/format";
import type { PlatformSettings } from "@/lib/types";

const GROUPS: { title: string; hint?: string; keys: string[] }[] = [
  {
    title: "Platform",
    hint: "Shown to customers in the storefront and on support messages.",
    keys: ["platform_name", "currency", "support_email", "support_phone"],
  },
  {
    title: "Commerce and fees",
    hint: "Commission is charged on merchandise only, never on delivery.",
    keys: ["commission_bp", "delivery_fee_flat", "free_delivery_threshold", "max_qty_per_line"],
  },
  {
    title: "Fulfilment",
    hint: "How long stock is held at checkout and how quickly suppliers should respond.",
    keys: ["reservation_ttl_minutes", "supplier_accept_sla_hours", "carrier_default"],
  },
  {
    title: "Returns",
    hint: "Applied to new return requests; open returns keep their original terms.",
    keys: ["return_window_days", "refund_delivery_on_return", "refund_delivery_on_supplier_rejection"],
  },
  {
    title: "Payouts",
    hint: "Supplier funds become eligible only after delivery plus the hold period.",
    keys: ["payout_hold_days", "payout_minimum"],
  },
];

type Draft = Record<string, string | number | boolean>;

function sameValue(a: string | number | boolean, b: string | number | boolean) {
  return String(a) === String(b);
}

export function OpsSettingsPanel() {
  const [data, setData] = useState<PlatformSettings | null>(null);
  const [initial, setInitial] = useState<Draft>({});
  const [draft, setDraft] = useState<Draft>({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const payload = await api<PlatformSettings>("/ops/config");
      setData(payload);
      setInitial(payload.values);
      setDraft(payload.values);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <Loading label="Loading platform settings…" />;
  if (!data) return <Alert kind="error">{error || "Settings unavailable."}</Alert>;

  const label = (key: string) => data.labels[key] ?? titleCase(key.replaceAll("_", " "));
  const changed = Object.keys(draft).filter((key) => !sameValue(draft[key], initial[key]));

  function update(key: string, value: string | number | boolean) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function save() {
    if (changed.length === 0) return;
    setBusy("save");
    setError("");
    setNotice("");
    try {
      const values: Draft = {};
      for (const key of changed) {
        const type = typeof data?.defaults[key];
        if (type === "number") {
          const parsed = Number(draft[key]);
          if (!Number.isFinite(parsed) || !Number.isInteger(parsed)) {
            throw new Error(`${label(key)} must be a whole number.`);
          }
          values[key] = parsed;
        } else if (type === "boolean") {
          values[key] = Boolean(draft[key]);
        } else {
          values[key] = String(draft[key]).trim();
        }
      }
      const result = await api<{ values: Draft }>("/ops/config", {
        method: "PUT",
        body: { values },
      });
      setInitial(result.values);
      setDraft(result.values);
      setNotice("Settings saved. New orders use the updated rules immediately.");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}
      {notice ? <Alert kind="success">{notice}</Alert> : null}

      <div className="spread">
        <p className="small muted">
          Every rule below is configuration, not code. Changes are recorded in the audit log.
        </p>
        <div className="btn-row">
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            disabled={busy !== ""}
            onClick={() => {
              setDraft(initial);
              setNotice("");
            }}
          >
            Discard
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={busy !== "" || changed.length === 0}
            onClick={save}
          >
            {busy === "save"
              ? "Saving…"
              : changed.length === 0
                ? "Save changes"
                : `Save ${changed.length} change${changed.length === 1 ? "" : "s"}`}
          </button>
        </div>
      </div>

      <div className="split">
        {GROUPS.map((group) => (
          <section key={group.title} className="card card-pad">
            <h2 style={{ fontSize: "1.02rem" }}>{group.title}</h2>
            {group.hint ? (
              <p className="small faint" style={{ marginTop: 4, marginBottom: 14 }}>
                {group.hint}
              </p>
            ) : null}
            <div className="stack">
              {group.keys.map((key) => {
                const type = typeof data.defaults[key];
                const isDirty = !sameValue(draft[key], initial[key]);
                const isDefault = sameValue(draft[key], data.defaults[key]);
                return (
                  <div key={key}>
                    <label className="field">
                      <span>
                        {label(key)}
                        {isDirty ? (
                          <span aria-hidden="true" style={{ marginLeft: 8 }}>
                            <Badge tone="amber">unsaved</Badge>
                          </span>
                        ) : null}
                      </span>
                      {type === "boolean" ? (
                        <label className="row small" style={{ gap: 8, paddingTop: 4 }}>
                          <input
                            type="checkbox"
                            checked={Boolean(draft[key])}
                            onChange={(event) => update(key, event.target.checked)}
                          />
                          {draft[key] ? "Enabled" : "Disabled"}
                        </label>
                      ) : type === "number" ? (
                        <input
                          type="number"
                          min={0}
                          value={String(draft[key])}
                          onChange={(event) => update(key, event.target.value)}
                        />
                      ) : (
                        <input
                          value={String(draft[key])}
                          onChange={(event) => update(key, event.target.value)}
                        />
                      )}
                    </label>
                    <div className="spread" style={{ marginTop: 4 }}>
                      <span className="small faint">
                        {key === "commission_bp" ? `${percent(Number(draft[key]))} of merchandise` : null}
                        {!isDefault ? ` Default: ${String(data.defaults[key])}` : null}
                      </span>
                      {!isDefault ? (
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          onClick={() => update(key, data.defaults[key])}
                        >
                          Restore default
                        </button>
                      ) : null}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
