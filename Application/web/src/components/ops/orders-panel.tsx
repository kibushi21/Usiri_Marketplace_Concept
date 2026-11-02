"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, StatusBadge } from "@/components/ui";
import { ShipmentTrackingForm } from "@/components/ops/shipment-tracking";
import { api } from "@/lib/api";
import { date, money, titleCase } from "@/lib/format";
import type { Order, OpsOrder } from "@/lib/types";

const STATUSES = ["", "pending_payment", "paid", "fulfilling", "completed", "cancelled"];

export function OpsOrdersPanel() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [status, setStatus] = useState("");
  const [query, setQuery] = useState("");
  const [input, setInput] = useState("");
  const [selected, setSelected] = useState<OpsOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ limit: "100" });
      if (status) params.set("status", status);
      if (query) params.set("q", query);
      const data = await api<{ items: Order[] }>(`/ops/orders?${params.toString()}`);
      setOrders(data.items);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoading(false);
    }
  }, [status, query]);

  useEffect(() => {
    void load();
  }, [load]);

  async function open(orderId: string) {
    setLoadingDetail(true);
    setError("");
    try {
      setSelected(await api<OpsOrder>(`/ops/orders/${orderId}`));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoadingDetail(false);
    }
  }

  if (selected) {
    return (
      <div className="stack">
        <div>
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>
            ← Back to orders
          </button>
        </div>
        <OrderDetail order={selected} onRefresh={() => void open(selected.id)} />
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="filter-bar">
        <div className="chip-row">
          {STATUSES.map((value) => (
            <button
              key={value || "all"}
              type="button"
              className={`chip${status === value ? " active" : ""}`}
              onClick={() => setStatus(value)}
            >
              {value ? titleCase(value) : "All statuses"}
            </button>
          ))}
        </div>
        <form
          className="search"
          onSubmit={(event) => {
            event.preventDefault();
            setQuery(input.trim());
          }}
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Order code or recipient"
            aria-label="Search orders"
          />
          <button type="submit" className="btn btn-secondary btn-sm">
            Search
          </button>
        </form>
      </div>

      {error ? <Alert kind="error">{error}</Alert> : null}
      {loadingDetail ? <Loading label="Opening the order…" /> : null}

      {loading ? (
        <Loading label="Loading orders…" />
      ) : orders.length === 0 ? (
        <p className="muted">No orders match.</p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Stage</th>
                <th>Payment</th>
                <th className="right">Total</th>
                <th className="right">Refunded</th>
                <th>Placed</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
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
                  <td className="right">{order.refunded_total ? money(order.refunded_total) : "—"}</td>
                  <td className="small faint">{date(order.placed_at)}</td>
                  <td className="right">
                    <button type="button" className="btn btn-secondary btn-sm" onClick={() => open(order.id)}>
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function OrderDetail({ order, onRefresh }: { order: OpsOrder; onRefresh: () => Promise<void> | void }) {
  return (
    <div className="stack">
      <div className="card card-pad">
        <div className="spread" style={{ alignItems: "flex-start" }}>
          <div>
            <div className="row" style={{ gap: 10 }}>
              <h2 style={{ fontSize: "1.3rem" }}>{order.code}</h2>
              <StatusBadge status={order.stage} />
              <StatusBadge status={order.payment_status} />
            </div>
            <p className="muted small" style={{ marginTop: 6 }}>
              Placed {date(order.placed_at)} · {order.item_count} items · {order.supplier_orders.length}{" "}
              supplier orders
            </p>
            {order.cancellation_reason ? (
              <p className="small" style={{ color: "var(--danger)", marginTop: 4 }}>
                Cancelled: {order.cancellation_reason}
              </p>
            ) : null}
          </div>
          <div className="right">
            <div className="tiny faint">Order total</div>
            <div className="price" style={{ fontSize: "1.35rem" }}>
              {money(order.total)}
            </div>
            {order.refunded_total > 0 ? (
              <div className="small muted">Refunded {money(order.refunded_total)}</div>
            ) : null}
          </div>
        </div>
      </div>

      <div className="split">
        <div className="stack">
          {order.supplier_orders.map((so) => (
            <section key={so.id} className="card">
              <div className="card-pad" style={{ paddingBottom: 12 }}>
                <div className="spread">
                  <div>
                    <div className="row" style={{ gap: 8 }}>
                      <strong>{so.supplier?.name ?? so.code}</strong>
                      <StatusBadge status={so.status} />
                    </div>
                    <div className="small faint" style={{ marginTop: 4 }}>
                      {so.code} · payout {titleCase(so.payout_status)}
                    </div>
                  </div>
                  <div className="small right">
                    <div>Merchandise {money(so.merchandise_total)}</div>
                    <div className="faint">
                      Commission {money(so.commission_amount)} ({so.commission_bp / 100}%)
                    </div>
                    <div>Payable {money(so.remaining_payable)}</div>
                  </div>
                </div>
              </div>
              <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Qty</th>
                      <th>Status</th>
                      <th className="right">Line total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {so.items.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <div style={{ fontWeight: 600 }}>{item.product_name}</div>
                          <div className="small faint">
                            {item.variant_name} · {item.sku}
                          </div>
                          {item.rejection_reason ? (
                            <div className="small" style={{ color: "var(--danger)" }}>
                              {item.rejection_reason}
                            </div>
                          ) : null}
                        </td>
                        <td>{item.qty}</td>
                        <td>
                          <StatusBadge status={item.status} />
                        </td>
                        <td className="right">{money(item.line_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {so.shipments.length > 0 ? (
                <div className="card-pad" style={{ borderTop: "1px solid var(--line)" }}>
                  <div className="tiny faint" style={{ marginBottom: 6 }}>
                    Shipments
                  </div>
                  {so.shipments.map((shipment) => {
                    const latest = shipment.events[shipment.events.length - 1];
                    return (
                      <div key={shipment.id} style={{ padding: "6px 0" }}>
                        <div className="spread small">
                          <span>
                            {shipment.carrier} · {shipment.tracking_number ?? "—"}{" "}
                            <StatusBadge status={shipment.status} />
                          </span>
                          <span className="faint">
                            {shipment.delivered_at
                              ? `Delivered ${date(shipment.delivered_at)}`
                              : shipment.booked_at
                                ? `Booked ${date(shipment.booked_at)}`
                                : ""}
                          </span>
                        </div>
                        <div className="spread" style={{ marginTop: 4, gap: 8, alignItems: "flex-start" }}>
                          <span className="tiny faint">
                            {latest
                              ? `${titleCase(latest.status)} · ${date(latest.occurred_at)}${
                                  latest.note ? ` · ${latest.note}` : ""
                                }`
                              : "No tracking events yet"}
                          </span>
                          <ShipmentTrackingForm shipment={shipment} onUpdated={onRefresh} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : null}
            </section>
          ))}

          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Payments</h3>
            {order.payments.length === 0 ? (
              <p className="muted small">No payment attempts.</p>
            ) : (
              <div className="table-wrap" style={{ border: "none" }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Provider</th>
                      <th>Reference</th>
                      <th>Method</th>
                      <th className="right">Amount</th>
                      <th>Status</th>
                      <th>Initiated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.payments.map((payment) => (
                      <tr key={payment.id}>
                        <td>{payment.provider}</td>
                        <td className="small" style={{ fontFamily: "ui-monospace, monospace" }}>
                          {payment.provider_ref ?? "—"}
                        </td>
                        <td>{titleCase(payment.method)}</td>
                        <td className="right">{money(payment.amount)}</td>
                        <td>
                          <StatusBadge status={payment.status} />
                        </td>
                        <td className="small faint">{date(payment.initiated_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {order.refunds.length > 0 ? (
            <section className="card card-pad">
              <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Refunds</h3>
              <div className="stack-sm">
                {order.refunds.map((refund) => (
                  <div key={refund.id} className="spread small">
                    <div>
                      <strong>{money(refund.amount)}</strong>
                      <div className="faint">
                        Merchandise {money(refund.merchandise_amount)} · delivery{" "}
                        {money(refund.delivery_amount)} · commission reversal{" "}
                        {money(refund.commission_reversal)}
                      </div>
                      <div className="faint">{refund.reason}</div>
                    </div>
                    <div className="right">
                      <StatusBadge status={refund.status} />
                      <div className="faint">{date(refund.completed_at ?? refund.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ) : null}

          {order.returns.length > 0 ? (
            <section className="card card-pad">
              <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Returns</h3>
              <div className="stack-sm">
                {order.returns.map((entry) => (
                  <div key={entry.id} className="spread small">
                    <div>
                      <strong>{entry.code}</strong> · {entry.qty} units · {titleCase(entry.reason)}
                    </div>
                    <StatusBadge status={entry.status} />
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </div>

        <div className="stack">
          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Customer</h3>
            {order.customer ? (
              <div className="small">
                <strong>{order.customer.full_name}</strong>
                <div className="muted">{order.customer.email}</div>
                <div className="muted">{order.customer.phone ?? "—"}</div>
              </div>
            ) : (
              <p className="muted small">Customer record unavailable.</p>
            )}
            <hr className="divider" />
            <div className="tiny faint" style={{ marginBottom: 6 }}>
              Delivery
            </div>
            <div className="small">
              <strong>{order.delivery_address.recipient_name}</strong>
              <div className="muted">{order.delivery_address.phone}</div>
              <div className="muted" style={{ marginTop: 4 }}>
                {[
                  order.delivery_address.street,
                  order.delivery_address.ward,
                  order.delivery_address.district,
                  order.delivery_address.region,
                ]
                  .filter(Boolean)
                  .join(", ")}
              </div>
              {order.delivery_address.landmark ? (
                <div className="faint">Near {order.delivery_address.landmark}</div>
              ) : null}
            </div>
            {order.notes ? (
              <>
                <hr className="divider" />
                <div className="tiny faint">Notes</div>
                <p className="small muted">{order.notes}</p>
              </>
            ) : null}
          </section>

          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Money</h3>
            <div className="summary-line">
              <span className="muted">Merchandise</span>
              <span>{money(order.subtotal)}</span>
            </div>
            <div className="summary-line">
              <span className="muted">Delivery</span>
              <span>{money(order.delivery_total)}</span>
            </div>
            <div className="summary-total">
              <span>Total</span>
              <span>{money(order.total)}</span>
            </div>
            {order.paid_at ? (
              <p className="small faint" style={{ marginTop: 8 }}>
                Paid {date(order.paid_at)}
              </p>
            ) : null}
          </section>

          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Audit trail</h3>
            {order.audit.length === 0 ? (
              <p className="muted small">No events recorded.</p>
            ) : (
              <div className="stack-sm">
                {order.audit.map((entry, index) => (
                  <div key={`${entry.action}-${index}`} className="small">
                    <div style={{ fontWeight: 600 }}>{entry.action}</div>
                    <div className="faint">
                      {entry.actor_role} · {date(entry.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
