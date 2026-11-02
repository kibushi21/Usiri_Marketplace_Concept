"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, Stat, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money } from "@/lib/format";
import type { OpsDashboard } from "@/lib/types";

export function OpsOverviewPanel({ onOpenOrders }: { onOpenOrders: () => void }) {
  const [data, setData] = useState<OpsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setData(await api<OpsDashboard>("/ops/dashboard"));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <Loading label="Loading the operations dashboard…" />;
  if (!data) return <Alert kind="error">{error || "Dashboard unavailable."}</Alert>;

  const summary = data.summary;

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="spread">
        <p className="small muted">
          Live position across orders, refunds and supplier balances. Figures come from the ledger.
        </p>
        <button type="button" className="btn btn-ghost btn-sm" onClick={load}>
          Refresh
        </button>
      </div>

      <div className="stat-grid">
        <Stat label="GMV" value={money(summary.gmv)} hint={`${summary.orders_paid} paid orders`} />
        <Stat label="Net GMV" value={money(summary.net_gmv)} hint={`Refunded ${money(summary.refunds)}`} />
        <Stat
          label="Commission earned"
          value={money(summary.commission_earned)}
          hint={`Delivery ${money(summary.delivery_earned)}`}
        />
        <Stat label="Supplier payable" value={money(summary.supplier_payable)} hint="Unsettled balance" />
        <Stat label="Cash at PSP" value={money(summary.cash_at_psp)} hint="Clearing account" />
        <Stat
          label="Pending payouts"
          value={money(summary.pending_payout_value)}
          hint={`${summary.pending_payouts} awaiting finance`}
        />
        <Stat
          label="Awaiting supplier"
          value={summary.awaiting_supplier_acceptance}
          hint="Orders not yet accepted"
        />
        <Stat label="Open returns" value={summary.open_returns} hint="Requested or approved" />
      </div>

      <section className="card">
        <div className="card-pad" style={{ paddingBottom: 12 }}>
          <div className="spread">
            <h2 style={{ fontSize: "1.02rem" }}>Orders waiting on suppliers</h2>
            <button type="button" className="btn btn-ghost btn-sm" onClick={onOpenOrders}>
              Open orders
            </button>
          </div>
        </div>
        {data.awaiting_acceptance.length === 0 ? (
          <div className="card-pad" style={{ paddingTop: 0 }}>
            <p className="muted small">Nothing waiting. Suppliers are keeping up.</p>
          </div>
        ) : (
          <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Supplier order</th>
                  <th>Supplier</th>
                  <th>Customer order</th>
                  <th>Lines</th>
                  <th className="right">Value</th>
                  <th>Received</th>
                </tr>
              </thead>
              <tbody>
                {data.awaiting_acceptance.map((entry) => (
                  <tr key={entry.id}>
                    <td style={{ fontWeight: 600 }}>{entry.code}</td>
                    <td>{entry.supplier ?? "—"}</td>
                    <td>{entry.order_code ?? "—"}</td>
                    <td>{entry.items}</td>
                    <td className="right">{money(entry.value)}</td>
                    <td className="small faint">{date(entry.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="split">
        <section className="card card-pad">
          <h2 style={{ fontSize: "1.02rem", marginBottom: 12 }}>Low stock</h2>
          {summary.low_stock.length === 0 ? (
            <p className="muted small">No variants at or below three available units.</p>
          ) : (
            <div className="table-wrap" style={{ border: "none" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>SKU</th>
                    <th className="right">On hand</th>
                    <th className="right">Reserved</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.low_stock.map((row) => (
                    <tr key={row.sku}>
                      <td>{row.product}</td>
                      <td className="small faint">{row.sku}</td>
                      <td className="right">{row.on_hand}</td>
                      <td className="right">{row.reserved}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="card card-pad">
          <h2 style={{ fontSize: "1.02rem", marginBottom: 12 }}>Top products by value</h2>
          {summary.top_products.length === 0 ? (
            <p className="muted small">No paid orders yet.</p>
          ) : (
            <div className="stack-sm">
              {summary.top_products.map((row) => (
                <div key={row.product} className="spread small">
                  <span style={{ maxWidth: "62%" }}>{row.product}</span>
                  <span className="right">
                    <strong>{money(row.value)}</strong>
                    <div className="faint">{row.qty} units</div>
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      <section className="card">
        <div className="card-pad" style={{ paddingBottom: 12 }}>
          <h2 style={{ fontSize: "1.02rem" }}>Recent orders</h2>
        </div>
        <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Stage</th>
                <th>Payment</th>
                <th className="right">Total</th>
                <th>Placed</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_orders.map((order) => (
                <tr key={order.id}>
                  <td style={{ fontWeight: 600 }}>{order.code}</td>
                  <td>{order.customer_name ?? "—"}</td>
                  <td>
                    <StatusBadge status={order.stage} />
                  </td>
                  <td>
                    <StatusBadge status={order.payment_status} />
                  </td>
                  <td className="right">{money(order.total)}</td>
                  <td className="small faint">{date(order.placed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
