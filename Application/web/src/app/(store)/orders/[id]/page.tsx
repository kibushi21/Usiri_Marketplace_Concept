"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { CargoTracking } from "@/components/cargo-tracking";
import { ChatThread } from "@/components/chat-thread";
import { Alert, BackLink, Loading, StatusBadge } from "@/components/ui";
import { api, idempotencyKey } from "@/lib/api";
import { date, money, titleCase } from "@/lib/format";
import type {
  ChatConversation,
  Order,
  OrderItem,
  Payment,
  Refund,
  ReturnRecord,
} from "@/lib/types";

const RETURN_REASONS = [
  { id: "damaged", label: "Arrived damaged" },
  { id: "wrong_item", label: "Wrong item delivered" },
  { id: "not_as_described", label: "Not as described" },
  { id: "faulty", label: "Faulty or not working" },
  { id: "changed_mind", label: "Changed my mind" },
  { id: "not_delivered", label: "Marked delivered but not received" },
];

export default function OrderDetailPage() {
  return (
    <RequireAuth roles={["customer"]}>
      <OrderDetail />
    </RequireAuth>
  );
}

function OrderDetail() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const [order, setOrder] = useState<Order | null>(null);
  const [refunds, setRefunds] = useState<Refund[]>([]);
  const [returns, setReturns] = useState<ReturnRecord[]>([]);
  const [chats, setChats] = useState<Record<string, string>>({});
  const [openChat, setOpenChat] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [returnItem, setReturnItem] = useState<OrderItem | null>(null);
  const [returnQty, setReturnQty] = useState(1);
  const [returnReason, setReturnReason] = useState("damaged");
  const [returnDetails, setReturnDetails] = useState("");

  const load = useCallback(
    async (silent = false) => {
      if (!silent) setLoading(true);
      try {
        const [orderData, refundData, returnData, chatData] = await Promise.all([
          api<Order>(`/orders/${params.id}`),
          api<{ items: Refund[] }>(`/orders/${params.id}/refunds`),
          api<{ items: ReturnRecord[] }>("/returns"),
          api<{ items: ChatConversation[] }>("/chats"),
        ]);
        setOrder(orderData);
        setRefunds(refundData.items);
        setReturns(returnData.items.filter((entry) => entry.order_id === params.id));
        setChats(
          Object.fromEntries(
            chatData.items
              .filter((entry) => entry.order_id === params.id)
              .map((entry) => [entry.supplier_order_id, entry.id]),
          ),
        );
      } catch (cause) {
        setError((cause as Error).message);
      } finally {
        setLoading(false);
      }
    },
    [params.id],
  );

  useEffect(() => {
    void load();
  }, [load]);

  async function payNow() {
    if (!order) return;
    setBusy("pay");
    setError("");
    try {
      const data = await api<{ payment: Payment }>(`/orders/${order.id}/payments`, {
        method: "POST",
        body: { method: "mobile_money", msisdn: order.delivery_address.phone },
        headers: { "Idempotency-Key": idempotencyKey() },
      });
      router.push(`/pay/${data.payment.id}`);
    } catch (cause) {
      setError((cause as Error).message);
      setBusy("");
    }
  }

  async function cancelOrder() {
    if (!order) return;
    if (!window.confirm(`Cancel ${order.code}? Any captured payment will be refunded through the provider.`)) {
      return;
    }
    setBusy("cancel");
    setError("");
    setNotice("");
    try {
      const updated = await api<Order>(
        `/orders/${order.id}/cancel?reason=${encodeURIComponent("Customer changed their mind")}`,
        { method: "POST" },
      );
      setOrder(updated);
      setNotice("Order cancelled. Any refunds are listed below.");
      await load(true);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function submitReturn() {
    if (!order || !returnItem) return;
    setBusy("return");
    setError("");
    setNotice("");
    try {
      await api<ReturnRecord>(`/orders/${order.id}/returns`, {
        method: "POST",
        body: {
          item_id: returnItem.id,
          qty: returnQty,
          reason: returnReason,
          details: returnDetails || null,
        },
      });
      setNotice("Return requested. Support will review it and arrange collection.");
      setReturnItem(null);
      setReturnDetails("");
      setReturnQty(1);
      await load(true);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (loading) return <Loading label="Loading the order…" />;
  if (!order) {
    return (
      <div className="container section">
        <Alert kind="error">{error || "Order not found."}</Alert>
        <p style={{ marginTop: 16 }}>
          <Link href="/orders" className="btn btn-secondary">
            Back to orders
          </Link>
        </p>
      </div>
    );
  }

  const timeline = buildTimeline(order);
  const cancellable = order.status === "pending_payment" || order.status === "paid";

  return (
    <div className="container portal-body">
      <div style={{ paddingTop: 18 }}>
        <BackLink href="/orders">All orders</BackLink>
      </div>

      <div className="portal-head" style={{ paddingTop: 4 }}>
        <div>
          <div className="row" style={{ gap: 10, marginBottom: 8 }}>
            <span className="tiny faint">Order</span>
            <StatusBadge status={order.stage} />
            {order.refunded_total > 0 ? <StatusBadge status={order.payment_status} /> : null}
          </div>
          <h1 style={{ fontFamily: "var(--font-serif)", fontWeight: 500 }}>{order.code}</h1>
          <p className="muted small" style={{ marginTop: 8 }}>
            Placed {date(order.placed_at)} · {order.item_count} item{order.item_count === 1 ? "" : "s"} ·{" "}
            {order.supplier_orders.length} supplier shipment{order.supplier_orders.length === 1 ? "" : "s"}
          </p>
        </div>
        <div className="btn-row">
          {order.stage === "awaiting_payment" ? (
            <button type="button" className="btn btn-primary" onClick={payNow} disabled={busy !== ""}>
              {busy === "pay" ? "Starting payment…" : `Pay ${money(order.total)}`}
            </button>
          ) : null}
          {cancellable ? (
            <button type="button" className="btn btn-danger" onClick={cancelOrder} disabled={busy !== ""}>
              {busy === "cancel" ? "Cancelling…" : "Cancel order"}
            </button>
          ) : null}
          <Link href="/support" className="btn btn-secondary">
            Get help
          </Link>
        </div>
      </div>

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}
      {notice ? <div style={{ marginBottom: 16 }}><Alert kind="success">{notice}</Alert></div> : null}

      <CargoTracking order={order} onRefresh={() => load(true)} />

      <div className="split">
        <div className="stack">
          {order.supplier_orders.map((so) => (
            <section key={so.id} className="card">
              <div className="card-pad" style={{ paddingBottom: 14 }}>
                <div className="spread" style={{ alignItems: "flex-start" }}>
                  <div>
                    <div className="row" style={{ gap: 10 }}>
                      <strong>{so.supplier?.name ?? "Supplier"}</strong>
                      <StatusBadge status={so.status} />
                      {chats[so.id] ? (
                        <button
                          type="button"
                          className="btn btn-ghost btn-sm"
                          aria-expanded={openChat === so.id}
                          onClick={() =>
                            setOpenChat((current) => (current === so.id ? null : so.id))
                          }
                        >
                          {openChat === so.id ? "Hide chat" : "Message"}
                        </button>
                      ) : null}
                    </div>
                    <div className="small faint" style={{ marginTop: 4 }}>
                      Shipment order {so.code} · {so.items.length} line
                      {so.items.length === 1 ? "" : "s"}
                    </div>
                  </div>
                  <div className="right small muted">
                    {so.shipments.length > 0 ? (
                      <>
                        <div>{so.shipments[so.shipments.length - 1].carrier}</div>
                        <div style={{ fontFamily: "ui-monospace, monospace" }}>
                          {so.shipments[so.shipments.length - 1].tracking_number ?? "—"}
                        </div>
                      </>
                    ) : (
                      <span>Not yet dispatched</span>
                    )}
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
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {so.items.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <div style={{ fontWeight: 600 }}>{item.product_name}</div>
                          <div className="small faint">
                            {item.variant_name} · {money(item.unit_price)}
                          </div>
                          {item.rejection_reason ? (
                            <div className="small" style={{ color: "var(--danger)", marginTop: 2 }}>
                              {item.rejection_reason}
                            </div>
                          ) : null}
                          {item.refunded_qty > 0 ? (
                            <div className="small faint">{item.refunded_qty} refunded</div>
                          ) : null}
                        </td>
                        <td>{item.qty}</td>
                        <td>
                          <StatusBadge status={item.status} />
                        </td>
                        <td className="right">{money(item.line_total)}</td>
                        <td className="right">
                          {item.returnable ? (
                            <button
                              type="button"
                              className="btn btn-secondary btn-sm"
                              onClick={() => {
                                setReturnItem(item);
                                setReturnQty(1);
                                setReturnReason("damaged");
                                setReturnDetails("");
                              }}
                            >
                              Return
                            </button>
                          ) : null}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {openChat === so.id && chats[so.id] ? (
                <div className="card-pad" style={{ paddingTop: 0 }}>
                  <ChatThread conversationId={chats[so.id]} />
                </div>
              ) : null}

              {returnItem && returnItem.supplier_order_id === so.id ? (
                <div className="card-pad" style={{ borderTop: "1px solid var(--line)", background: "var(--surface-2)" }}>
                  <div className="spread" style={{ marginBottom: 12 }}>
                    <strong style={{ fontSize: ".95rem" }}>Return {returnItem.product_name}</strong>
                    <button type="button" className="btn btn-ghost btn-sm" onClick={() => setReturnItem(null)}>
                      Close
                    </button>
                  </div>
                  <div className="form-grid">
                    <label className="field">
                      <span>Quantity</span>
                      <input
                        type="number"
                        min={1}
                        max={returnItem.qty - returnItem.refunded_qty}
                        value={returnQty}
                        onChange={(event) => setReturnQty(Number(event.target.value))}
                      />
                    </label>
                    <label className="field">
                      <span>Reason</span>
                      <select value={returnReason} onChange={(event) => setReturnReason(event.target.value)}>
                        {RETURN_REASONS.map((reason) => (
                          <option key={reason.id} value={reason.id}>
                            {reason.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="field span-2">
                      <span>Details (optional)</span>
                      <textarea
                        value={returnDetails}
                        onChange={(event) => setReturnDetails(event.target.value)}
                        placeholder="Describe the problem so support can assess it"
                      />
                    </label>
                  </div>
                  <button
                    type="button"
                    className="btn btn-primary"
                    style={{ marginTop: 14 }}
                    onClick={submitReturn}
                    disabled={busy === "return"}
                  >
                    {busy === "return" ? "Submitting…" : "Request return"}
                  </button>
                </div>
              ) : null}
            </section>
          ))}

          {returns.length > 0 ? (
            <section className="card card-pad">
              <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Returns on this order</h2>
              <div className="stack-sm">
                {returns.map((entry) => (
                  <div key={entry.id} className="row-card" style={{ padding: "12px 14px" }}>
                    <div className="spread">
                      <div>
                        <strong style={{ fontSize: ".92rem" }}>
                          {entry.item?.product_name ?? "Item"} × {entry.qty}
                        </strong>
                        <div className="small faint">
                          {entry.code} · {titleCase(entry.reason)} · requested {date(entry.requested_at)}
                        </div>
                        {entry.decision_note ? <div className="small muted">{entry.decision_note}</div> : null}
                      </div>
                      <div className="right">
                        <StatusBadge status={entry.status} />
                        {entry.refund_amount ? (
                          <div className="small muted" style={{ marginTop: 4 }}>
                            {money(entry.refund_amount)}
                          </div>
                        ) : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ) : null}

          {refunds.length > 0 ? (
            <section className="card card-pad">
              <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Refunds</h2>
              <div className="stack-sm">
                {refunds.map((refund) => (
                  <div key={refund.id} className="spread small">
                    <div>
                      <strong>{money(refund.amount)}</strong>
                      <div className="faint">{refund.reason}</div>
                    </div>
                    <div className="right">
                      <StatusBadge status={refund.status} />
                      <div className="faint" style={{ marginTop: 4 }}>
                        {date(refund.completed_at ?? refund.created_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ) : null}
        </div>

        <aside className="stack">
          <section className="card card-pad">
            <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Order timeline</h2>
            <div className="timeline">
              {timeline.map((event, index) => (
                <div key={`${event.label}-${index}`} className="timeline-item">
                  <span className={`timeline-dot ${index === timeline.length - 1 ? "current" : "done"}`} />
                  <div>
                    <div style={{ fontSize: ".92rem", fontWeight: 600 }}>{event.label}</div>
                    <div className="small faint">{event.detail ? `${event.detail} · ` : ""}{date(event.at)}</div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="card card-pad">
            <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Payment summary</h2>
            <div className="summary-line">
              <span className="muted">Merchandise</span>
              <span>{money(order.subtotal)}</span>
            </div>
            <div className="summary-line">
              <span className="muted">Delivery</span>
              <span>{money(order.delivery_total)}</span>
            </div>
            {order.refunded_total > 0 ? (
              <div className="summary-line">
                <span className="muted">Refunded</span>
                <span>−{money(order.refunded_total)}</span>
              </div>
            ) : null}
            <div className="summary-total">
              <span>Total</span>
              <span>{money(order.total)}</span>
            </div>
            <p className="small faint" style={{ marginTop: 10 }}>
              Payment status: {titleCase(order.payment_status)}
            </p>
          </section>

          <section className="card card-pad">
            <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Delivery address</h2>
            <div className="small">
              <strong>{order.delivery_address.recipient_name}</strong>
              <div className="muted">{order.delivery_address.phone}</div>
              <div className="muted" style={{ marginTop: 6 }}>
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
                <div className="faint" style={{ marginTop: 4 }}>
                  Near {order.delivery_address.landmark}
                </div>
              ) : null}
            </div>
            {order.notes ? (
              <>
                <hr className="divider" />
                <div className="tiny faint">Notes</div>
                <p className="small muted" style={{ marginTop: 4 }}>
                  {order.notes}
                </p>
              </>
            ) : null}
          </section>
        </aside>
      </div>
    </div>
  );
}

function buildTimeline(order: Order): { label: string; detail?: string; at: string }[] {
  const events: { label: string; detail?: string; at: string }[] = [
    { label: "Order placed", at: order.placed_at },
  ];
  if (order.paid_at) events.push({ label: "Payment captured", at: order.paid_at });
  for (const so of order.supplier_orders) {
    if (so.accepted_at) {
      events.push({
        label: `Supplier accepted (${so.supplier?.name ?? so.code})`,
        at: so.accepted_at,
      });
    }
    for (const shipment of so.shipments) {
      if (shipment.booked_at) {
        events.push({
          label: `Dispatched with ${shipment.carrier}`,
          detail: shipment.tracking_number ?? undefined,
          at: shipment.booked_at,
        });
      }
      if (shipment.delivered_at) {
        events.push({ label: "Delivered", at: shipment.delivered_at });
      }
    }
  }
  if (order.completed_at) events.push({ label: "Order completed", at: order.completed_at });
  if (order.cancelled_at) {
    events.push({ label: "Order cancelled", detail: order.cancellation_reason ?? undefined, at: order.cancelled_at });
  }
  return events.sort((a, b) => new Date(a.at).getTime() - new Date(b.at).getTime());
}
