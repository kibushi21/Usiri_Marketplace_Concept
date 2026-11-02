"use client";

import { useState } from "react";

import { Alert, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money, titleCase } from "@/lib/format";
import type { SupplierOrder } from "@/lib/types";

export function SupplierOrdersPanel({
  orders,
  onChanged,
  filter,
}: {
  orders: SupplierOrder[];
  onChanged: () => Promise<void>;
  filter: string;
}) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const visible = filter === "all" ? orders : orders.filter((order) => order.status === filter);

  if (visible.length === 0) {
    return <p className="muted">No orders in this state.</p>;
  }

  return (
    <div className="stack-sm">
      {visible.map((order) => {
        const open = expanded === order.id;
        return (
          <article key={order.id} className="card">
            <button
              type="button"
              className="spread"
              style={{
                width: "100%",
                textAlign: "left",
                background: "none",
                border: "none",
                padding: "16px 18px",
                cursor: "pointer",
                font: "inherit",
              }}
              onClick={() => setExpanded(open ? null : order.id)}
            >
              <div>
                <div className="row" style={{ gap: 10 }}>
                  <strong>{order.code}</strong>
                  <StatusBadge status={order.status} />
                  {order.payout_status !== "unpaid" ? (
                    <span className="badge badge-neutral">Payout {titleCase(order.payout_status)}</span>
                  ) : null}
                </div>
                <div className="small muted" style={{ marginTop: 5 }}>
                  Customer order {order.order?.code ?? order.order_id.slice(0, 8)} ·{" "}
                  {order.order?.customer_name ?? "Customer"} ·{" "}
                  {order.order?.placed_at ? date(order.order.placed_at) : date(order.accepted_at)}
                </div>
                <div className="small faint" style={{ marginTop: 3 }}>
                  {order.items.length} line{order.items.length === 1 ? "" : "s"} ·{" "}
                  {order.order?.delivery_address?.region ?? "—"}
                </div>
              </div>
              <div className="right">
                <div className="price">{money(order.merchandise_total)}</div>
                <div className="small faint">
                  You receive {money(order.supplier_payable)}
                </div>
                <div className="small" style={{ color: "var(--brand)", marginTop: 6 }}>
                  {open ? "Hide details" : "Manage →"}
                </div>
              </div>
            </button>

            {open ? (
              <div style={{ borderTop: "1px solid var(--line)" }}>
                <OrderWorkspace order={order} onChanged={onChanged} />
              </div>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function OrderWorkspace({
  order,
  onChanged,
}: {
  order: SupplierOrder;
  onChanged: () => Promise<void>;
}) {
  const awaiting = order.status === "awaiting_acceptance";
  const pendingItems = order.items.filter((item) => item.status === "pending");

  const [checked, setChecked] = useState<string[]>(pendingItems.map((item) => item.id));
  const [rejectReason, setRejectReason] = useState("Items are not available");
  const [carrier, setCarrier] = useState("");
  const [tracking, setTracking] = useState("");
  const [fee, setFee] = useState("");
  const [pod, setPod] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function run(label: string, request: () => Promise<unknown>, message: string) {
    setBusy(label);
    setError("");
    setNotice("");
    try {
      await request();
      setNotice(message);
      await onChanged();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  const accept = () =>
    run(
      "accept",
      () =>
        api(`/supplier/orders/${order.id}/accept`, {
          method: "POST",
          body: { accepted_item_ids: checked, rejection_reason: rejectReason },
        }),
      checked.length === pendingItems.length
        ? "Order accepted. Prepare it and mark it ready when it can be dispatched."
        : "Selected items accepted; the rest were rejected and refunded to the customer.",
    );

  const reject = () =>
    run(
      "reject",
      () =>
        api(`/supplier/orders/${order.id}/reject`, {
          method: "POST",
          body: { reason: rejectReason },
        }),
      "Order rejected. The customer has been refunded through the original payment method.",
    );

  const ready = () =>
    run("ready", () => api(`/supplier/orders/${order.id}/ready`, { method: "POST" }), "Marked ready for dispatch.");

  const ship = () =>
    run(
      "ship",
      () =>
        api(`/supplier/orders/${order.id}/ship`, {
          method: "POST",
          body: {
            carrier: carrier.trim() || null,
            tracking_number: tracking.trim() || null,
            fee: fee ? Number(fee) : null,
          },
        }),
      "Shipment booked. The customer can now see the tracking reference.",
    );

  const deliver = () =>
    run(
      "deliver",
      () =>
        api(`/supplier/orders/${order.id}/deliver`, {
          method: "POST",
          body: { pod_ref: pod.trim() || null, note: null },
        }),
      "Delivery recorded. The payout hold now starts.",
    );

  return (
    <div>
      <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
        <table className="table">
          <thead>
            <tr>
              {awaiting ? <th style={{ width: 34 }} /> : null}
              <th>Item</th>
              <th>Qty</th>
              <th className="right">Unit</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map((item) => (
              <tr key={item.id}>
                {awaiting ? (
                  <td>
                    {item.status === "pending" ? (
                      <input
                        type="checkbox"
                        checked={checked.includes(item.id)}
                        onChange={(event) =>
                          setChecked((current) =>
                            event.target.checked
                              ? [...current, item.id]
                              : current.filter((id) => id !== item.id),
                          )
                        }
                        style={{ width: 16, height: 16, accentColor: "var(--brand)" }}
                        aria-label={`Accept ${item.product_name}`}
                      />
                    ) : null}
                  </td>
                ) : null}
                <td>
                  <div style={{ fontWeight: 600 }}>{item.product_name}</div>
                  <div className="small faint">
                    {item.variant_name} · {item.sku}
                  </div>
                </td>
                <td>{item.qty}</td>
                <td className="right">{money(item.unit_price)}</td>
                <td>
                  <StatusBadge status={item.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card-pad" style={{ background: "var(--surface-2)" }}>
        <div className="kv" style={{ marginBottom: 14 }}>
          <div>
            <span>Merchandise</span>
            <strong>{money(order.merchandise_total)}</strong>
          </div>
          <div>
            <span>Commission</span>
            <strong>
              {money(order.commission_amount)} ({order.commission_bp / 100}%)
            </strong>
          </div>
          <div>
            <span>Delivery collected</span>
            <strong>{money(order.delivery_fee)}</strong>
          </div>
          <div>
            <span>Payable</span>
            <strong>{money(order.supplier_payable)}</strong>
          </div>
        </div>

        {order.order?.delivery_address ? (
          <p className="small muted" style={{ marginBottom: 14 }}>
            Deliver to {order.order.delivery_address.recipient_name} ·{" "}
            {order.order.delivery_address.phone} ·{" "}
            {[
              order.order.delivery_address.street,
              order.order.delivery_address.ward,
              order.order.delivery_address.district,
              order.order.delivery_address.region,
            ]
              .filter(Boolean)
              .join(", ")}
          </p>
        ) : null}

        {error ? <div style={{ marginBottom: 12 }}><Alert kind="error">{error}</Alert></div> : null}
        {notice ? <div style={{ marginBottom: 12 }}><Alert kind="success">{notice}</Alert></div> : null}

        {awaiting ? (
          <div className="stack-sm">
            <label className="field" style={{ maxWidth: 420 }}>
              <span>Reason used if you reject a line</span>
              <input value={rejectReason} onChange={(event) => setRejectReason(event.target.value)} />
            </label>
            <div className="btn-row">
              <button
                type="button"
                className="btn btn-primary"
                onClick={accept}
                disabled={busy !== "" || checked.length === 0}
              >
                {busy === "accept" ? "Accepting…" : `Accept ${checked.length} of ${pendingItems.length}`}
              </button>
              <button type="button" className="btn btn-danger" onClick={reject} disabled={busy !== ""}>
                {busy === "reject" ? "Rejecting…" : "Reject the whole order"}
              </button>
            </div>
          </div>
        ) : null}

        {order.status === "accepted" ? (
          <div className="btn-row">
            <button type="button" className="btn btn-secondary" onClick={ready} disabled={busy !== ""}>
              {busy === "ready" ? "Saving…" : "Mark ready for dispatch"}
            </button>
          </div>
        ) : null}

        {["accepted", "ready"].includes(order.status) ? (
          <div style={{ marginTop: 14 }}>
            <div className="tiny faint" style={{ marginBottom: 8 }}>
              Book a shipment
            </div>
            <div className="inline-form">
              <label className="field">
                <span>Carrier</span>
                <input
                  value={carrier}
                  onChange={(event) => setCarrier(event.target.value)}
                  placeholder="Leave blank for the default carrier"
                />
              </label>
              <label className="field">
                <span>Tracking (optional)</span>
                <input
                  value={tracking}
                  onChange={(event) => setTracking(event.target.value)}
                  placeholder="Auto-booked if blank"
                />
              </label>
              <label className="field" style={{ maxWidth: 140 }}>
                <span>Fee (TZS)</span>
                <input
                  type="number"
                  min={0}
                  value={fee}
                  onChange={(event) => setFee(event.target.value)}
                  placeholder={String(order.delivery_fee)}
                />
              </label>
              <button type="button" className="btn btn-primary" onClick={ship} disabled={busy !== ""}>
                {busy === "ship" ? "Booking…" : "Dispatch"}
              </button>
            </div>
          </div>
        ) : null}

        {order.status === "in_transit" ? (
          <div>
            <div className="tiny faint" style={{ marginBottom: 8 }}>
              Record delivery
            </div>
            <div className="inline-form">
              <label className="field">
                <span>Proof-of-delivery reference</span>
                <input
                  value={pod}
                  onChange={(event) => setPod(event.target.value)}
                  placeholder="Recipient name, OTP or POD ref"
                />
              </label>
              <button type="button" className="btn btn-primary" onClick={deliver} disabled={busy !== ""}>
                {busy === "deliver" ? "Saving…" : "Mark delivered"}
              </button>
            </div>
          </div>
        ) : null}

        {order.shipments.length > 0 ? (
          <div style={{ marginTop: 16 }}>
            <div className="tiny faint" style={{ marginBottom: 6 }}>
              Shipments
            </div>
            {order.shipments.map((shipment) => (
              <div key={shipment.id} className="spread small" style={{ padding: "4px 0" }}>
                <span>
                  {shipment.carrier} · {shipment.tracking_number ?? "no tracking"} ·{" "}
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
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
