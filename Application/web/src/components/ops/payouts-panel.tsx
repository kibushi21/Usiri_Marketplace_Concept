"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, Stat, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money } from "@/lib/format";
import type { Payout, PayoutBalance } from "@/lib/types";

interface EligibleRow {
  supplier: {
    id: string;
    code: string;
    trading_name: string;
    legal_name: string;
    region: string;
    status: string;
  };
  balance: PayoutBalance;
}

export function OpsPayoutsPanel() {
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [eligible, setEligible] = useState<EligibleRow[]>([]);
  const [busy, setBusy] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    const [payoutData, eligibleData] = await Promise.all([
      api<{ items: Payout[] }>("/ops/payouts"),
      api<{ items: EligibleRow[] }>("/ops/payouts/eligible"),
    ]);
    setPayouts(payoutData.items);
    setEligible(eligibleData.items);
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

  async function act(label: string, request: () => Promise<unknown>, message: string) {
    setBusy(label);
    setError("");
    setNotice("");
    try {
      await request();
      await load();
      setNotice(message);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (loading) return <Loading label="Loading payouts…" />;

  const pending = payouts.filter((payout) => payout.status === "pending_approval");
  const awaitingPayment = payouts.filter((payout) => payout.status === "approved");

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}
      {notice ? <Alert kind="success">{notice}</Alert> : null}

      <div className="stat-grid">
        <Stat label="Eligible suppliers" value={eligible.length} hint="Cleared the payout hold" />
        <Stat
          label="Eligible value"
          value={money(eligible.reduce((total, row) => total + row.balance.eligible, 0))}
        />
        <Stat label="Awaiting approval" value={pending.length} />
        <Stat label="Approved, not sent" value={awaitingPayment.length} />
      </div>

      <section className="card">
        <div className="card-pad" style={{ paddingBottom: 12 }}>
          <h2 style={{ fontSize: "1.02rem" }}>Eligible balances</h2>
          <p className="small faint" style={{ marginTop: 4 }}>
            A payout covers every eligible supplier order. The maker and checker must be different
            accounts.
          </p>
        </div>
        {eligible.length === 0 ? (
          <div className="card-pad" style={{ paddingTop: 0 }}>
            <p className="muted small">No supplier has an eligible balance above the minimum.</p>
          </div>
        ) : (
          <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Region</th>
                  <th className="right">Eligible</th>
                  <th className="right">In payout</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {eligible.map((row) => (
                  <tr key={row.supplier.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{row.supplier.trading_name}</div>
                      <div className="small faint">{row.supplier.code}</div>
                    </td>
                    <td>{row.supplier.region}</td>
                    <td className="right">{money(row.balance.eligible)}</td>
                    <td className="right">{money(row.balance.in_payout)}</td>
                    <td className="right">
                      <button
                        type="button"
                        className="btn btn-primary btn-sm"
                        disabled={busy !== ""}
                        onClick={() =>
                          act(
                            `request-${row.supplier.id}`,
                            () =>
                              api("/ops/payouts", {
                                method: "POST",
                                body: { supplier_id: row.supplier.id },
                              }),
                            `Payout requested for ${row.supplier.trading_name}.`,
                          )
                        }
                      >
                        {busy === `request-${row.supplier.id}` ? "Requesting…" : "Request payout"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="card">
        <div className="card-pad" style={{ paddingBottom: 12 }}>
          <h2 style={{ fontSize: "1.02rem" }}>Payouts</h2>
        </div>
        {payouts.length === 0 ? (
          <div className="card-pad" style={{ paddingTop: 0 }}>
            <p className="muted small">No payouts yet.</p>
          </div>
        ) : (
          <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Period</th>
                  <th className="right">Amount</th>
                  <th>Status</th>
                  <th>Reference</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {payouts.map((payout) => (
                  <tr key={payout.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{payout.supplier_name ?? payout.supplier_id.slice(0, 8)}</div>
                      <div className="small faint">{date(payout.created_at)}</div>
                    </td>
                    <td className="small muted">
                      {date(payout.period_start)} – {date(payout.period_end)}
                    </td>
                    <td className="right">{money(payout.amount)}</td>
                    <td>
                      <StatusBadge status={payout.status} />
                      {payout.rejection_reason ? (
                        <div className="small" style={{ color: "var(--danger)" }}>
                          {payout.rejection_reason}
                        </div>
                      ) : null}
                    </td>
                    <td className="small" style={{ fontFamily: "ui-monospace, monospace" }}>
                      {payout.provider_ref ?? "—"}
                    </td>
                    <td className="right">
                      <div className="btn-row" style={{ justifyContent: "flex-end" }}>
                        {payout.status === "pending_approval" ? (
                          <>
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              disabled={busy !== ""}
                              onClick={() =>
                                act(
                                  `approve-${payout.id}`,
                                  () =>
                                    api(`/ops/payouts/${payout.id}/approve`, {
                                      method: "POST",
                                      body: {},
                                    }),
                                  "Payout approved. A checker can now send it.",
                                )
                              }
                            >
                              {busy === `approve-${payout.id}` ? "Approving…" : "Approve"}
                            </button>
                            <button
                              type="button"
                              className="btn btn-danger btn-sm"
                              disabled={busy !== ""}
                              onClick={() => {
                                const reason = window.prompt("Reason for rejecting this payout", "Needs review");
                                if (!reason) return;
                                void act(
                                  `reject-${payout.id}`,
                                  () =>
                                    api(`/ops/payouts/${payout.id}/reject`, {
                                      method: "POST",
                                      body: { reason },
                                    }),
                                  "Payout rejected and supplier orders released.",
                                );
                              }}
                            >
                              Reject
                            </button>
                          </>
                        ) : null}
                        {payout.status === "approved" ? (
                          <button
                            type="button"
                            className="btn btn-primary btn-sm"
                            disabled={busy !== ""}
                            onClick={() =>
                              act(
                                `execute-${payout.id}`,
                                () => api(`/ops/payouts/${payout.id}/execute`, { method: "POST" }),
                                "Payout sent to the supplier's payout provider.",
                              )
                            }
                          >
                            {busy === `execute-${payout.id}` ? "Sending…" : "Send payout"}
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
