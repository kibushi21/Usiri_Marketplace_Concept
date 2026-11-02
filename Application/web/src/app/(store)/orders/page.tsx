"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { Alert, Empty, Loading, PageHead, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { money, date, titleCase } from "@/lib/format";
import type { Order } from "@/lib/types";

const FILTERS = [
  { id: "all", label: "All orders" },
  { id: "awaiting_payment", label: "Awaiting payment" },
  { id: "active", label: "In progress" },
  { id: "delivered", label: "Delivered" },
  { id: "cancelled", label: "Cancelled" },
];

export default function OrdersPage() {
  return (
    <RequireAuth roles={["customer"]}>
      <OrdersView />
    </RequireAuth>
  );
}

function OrdersView() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    api<{ items: Order[] }>("/orders")
      .then((data) => {
        if (active) setOrders(data.items);
      })
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const visible = orders.filter((order) => {
    if (filter === "all") return true;
    if (filter === "active") return ["awaiting_supplier", "preparing", "in_transit", "fulfilling"].includes(order.stage);
    return order.stage === filter;
  });

  return (
    <div className="container portal-body">
      <PageHead
        title="Your orders"
        description="Every order is tracked per supplier shipment. Open an order to see what each supplier is doing."
        actions={
          <Link href="/shop" className="btn btn-secondary btn-sm">
            Shop again
          </Link>
        }
      />

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}

      {loading ? (
        <Loading label="Loading your orders…" />
      ) : orders.length === 0 ? (
        <Empty
          title="No orders yet"
          action={
            <Link href="/shop" className="btn btn-primary">
              Start shopping
            </Link>
          }
        >
          When you place an order it will appear here with its payment and delivery progress.
        </Empty>
      ) : (
        <>
          <div className="chip-row" style={{ marginBottom: 18 }}>
            {FILTERS.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`chip${filter === option.id ? " active" : ""}`}
                onClick={() => setFilter(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>

          {visible.length === 0 ? (
            <p className="muted">No orders in this state.</p>
          ) : (
            <div className="stack-sm">
              {visible.map((order) => (
                <Link key={order.id} href={`/orders/${order.id}`} className="row-card" style={{ display: "block" }}>
                  <div className="spread" style={{ alignItems: "flex-start", gap: 18 }}>
                    <div>
                      <div className="row" style={{ gap: 10 }}>
                        <strong>{order.code}</strong>
                        <StatusBadge status={order.stage} />
                        {order.payment_status !== "paid" && order.payment_status !== "unpaid" ? (
                          <StatusBadge status={order.payment_status} />
                        ) : null}
                      </div>
                      <div className="small muted" style={{ marginTop: 6 }}>
                        Placed {date(order.placed_at)} · {order.item_count} item
                        {order.item_count === 1 ? "" : "s"} from {order.supplier_orders.length}{" "}
                        {order.supplier_orders.length === 1 ? "supplier" : "suppliers"}
                      </div>
                      <div className="small faint" style={{ marginTop: 4 }}>
                        {order.supplier_orders.map((so) => `${so.supplier?.name ?? "Supplier"} · ${titleCase(so.status)}`).join("  |  ")}
                      </div>
                    </div>
                    <div className="right">
                      <div className="price">{money(order.total)}</div>
                      {order.refunded_total > 0 ? (
                        <div className="small muted">Refunded {money(order.refunded_total)}</div>
                      ) : null}
                      <div className="small" style={{ color: "var(--brand)", marginTop: 6 }}>
                        View order →
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
