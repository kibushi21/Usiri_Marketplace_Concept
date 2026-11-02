"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Badge, Loading, Stat } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money, titleCase } from "@/lib/format";
import type { LedgerView } from "@/lib/types";

export function OpsLedgerPanel() {
  const [data, setData] = useState<LedgerView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setData(await api<LedgerView>("/ops/ledger"));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <Loading label="Reading the ledger…" />;
  if (!data) return <Alert kind="error">{error || "Ledger unavailable."}</Alert>;

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="spread">
        <div className="row" style={{ gap: 10 }}>
          <h2 style={{ fontSize: "1.05rem" }}>Accounts</h2>
          <Badge tone={data.balanced ? "green" : "red"}>
            {data.balanced ? "Debits equal credits" : "Out of balance"}
          </Badge>
        </div>
        <button type="button" className="btn btn-ghost btn-sm" onClick={load}>
          Refresh
        </button>
      </div>

      <div className="stat-grid">
        {data.balances.map((account) => (
          <Stat
            key={account.code}
            label={account.name}
            value={money(account.balance)}
            hint={`${titleCase(account.kind)} · ${account.code}`}
          />
        ))}
      </div>

      <section className="card">
        <div className="card-pad" style={{ paddingBottom: 12 }}>
          <h2 style={{ fontSize: "1.02rem" }}>Recent transactions</h2>
          <p className="small faint" style={{ marginTop: 4 }}>
            Every capture, refund and payout posts once with a unique reference, so a retried
            provider callback cannot double count.
          </p>
        </div>
        {data.transactions.length === 0 ? (
          <div className="card-pad" style={{ paddingTop: 0 }}>
            <p className="muted small">No transactions posted yet.</p>
          </div>
        ) : (
          <div className="stack-sm" style={{ padding: "0 20px 20px" }}>
            {data.transactions.map((transaction) => {
              const debit = transaction.entries.reduce((total, entry) => total + entry.debit, 0);
              const credit = transaction.entries.reduce((total, entry) => total + entry.credit, 0);
              return (
                <details key={transaction.id} className="card card-pad">
                  <summary style={{ cursor: "pointer" }}>
                    <span className="spread">
                      <span className="row" style={{ gap: 10 }}>
                        <strong style={{ fontSize: ".92rem" }}>{titleCase(transaction.kind)}</strong>
                        <span className="small faint">{date(transaction.created_at)}</span>
                        {debit === credit ? null : <Badge tone="red">unbalanced</Badge>}
                      </span>
                      <span className="price" style={{ fontSize: ".92rem" }}>
                        {money(debit)}
                      </span>
                    </span>
                    <span className="small faint" style={{ display: "block", marginTop: 4 }}>
                      {transaction.memo ?? transaction.reference}
                    </span>
                  </summary>
                  <div className="table-wrap" style={{ marginTop: 12, border: "none" }}>
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Account</th>
                          <th className="right">Debit</th>
                          <th className="right">Credit</th>
                        </tr>
                      </thead>
                      <tbody>
                        {transaction.entries.map((entry, index) => (
                          <tr key={`${transaction.id}-${entry.account}-${index}`}>
                            <td>{titleCase(entry.account.replaceAll("_", " "))}</td>
                            <td className="right">{entry.debit ? money(entry.debit) : "—"}</td>
                            <td className="right">{entry.credit ? money(entry.credit) : "—"}</td>
                          </tr>
                        ))}
                        <tr>
                          <td className="small faint">Total</td>
                          <td className="right small faint">{money(debit)}</td>
                          <td className="right small faint">{money(credit)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <p className="small faint" style={{ marginTop: 8, fontFamily: "ui-monospace, monospace" }}>
                    {transaction.reference}
                  </p>
                </details>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
