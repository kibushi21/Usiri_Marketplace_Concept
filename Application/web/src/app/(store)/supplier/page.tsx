"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { ChatInbox } from "@/components/chat-inbox";
import { SupplierOrdersPanel } from "@/components/supplier/orders-panel";
import { SupplierProductsPanel } from "@/components/supplier/products-panel";
import { Alert, Loading, PageHead, Stat, StatusBadge, Tabs } from "@/components/ui";
import { api } from "@/lib/api";
import { date, money, percent, titleCase } from "@/lib/format";
import type {
  Department,
  Payout,
  ReturnRecord,
  SupplierDashboard,
  SupplierOrder,
  SupplierProduct,
} from "@/lib/types";

type TabId = "overview" | "orders" | "messages" | "products" | "payouts" | "returns";

const TABS: { id: TabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "orders", label: "Orders" },
  { id: "messages", label: "Messages" },
  { id: "products", label: "Products" },
  { id: "payouts", label: "Payouts" },
  { id: "returns", label: "Returns" },
];

const ORDER_FILTERS = [
  "all",
  "awaiting_acceptance",
  "accepted",
  "ready",
  "in_transit",
  "delivered",
  "completed",
  "cancelled",
];

export default function SupplierPage() {
  return (
    <RequireAuth roles={["supplier"]}>
      <SupplierPortal />
    </RequireAuth>
  );
}

function SupplierPortal() {
  const [tab, setTab] = useState<TabId>("overview");
  const [dashboard, setDashboard] = useState<SupplierDashboard | null>(null);
  const [orders, setOrders] = useState<SupplierOrder[]>([]);
  const [products, setProducts] = useState<SupplierProduct[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [returns, setReturns] = useState<ReturnRecord[]>([]);
  const [orderFilter, setOrderFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAll = useCallback(async () => {
    const [dashboardData, orderData, productData, payoutData, returnData, departmentData] =
      await Promise.all([
        api<SupplierDashboard>("/supplier/dashboard"),
        api<{ items: SupplierOrder[] }>("/supplier/orders"),
        api<{ items: SupplierProduct[] }>("/supplier/products"),
        api<{ items: Payout[] }>("/supplier/payouts"),
        api<{ items: ReturnRecord[] }>("/supplier/returns"),
        api<Department[]>("/catalogue/departments", { auth: false }),
      ]);
    setDashboard(dashboardData);
    setOrders(orderData.items);
    setProducts(productData.items);
    setPayouts(payoutData.items);
    setReturns(returnData.items);
    setDepartments(departmentData);
  }, []);

  const reloadOrders = useCallback(async () => {
    const [orderData, dashboardData] = await Promise.all([
      api<{ items: SupplierOrder[] }>("/supplier/orders"),
      api<SupplierDashboard>("/supplier/dashboard"),
    ]);
    setOrders(orderData.items);
    setDashboard(dashboardData);
  }, []);

  const reloadProducts = useCallback(async () => {
    const data = await api<{ items: SupplierProduct[] }>("/supplier/products");
    setProducts(data.items);
  }, []);

  useEffect(() => {
    let active = true;
    loadAll()
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadAll]);

  if (loading) return <Loading label="Opening your supplier portal…" />;
  if (!dashboard) {
    return (
      <div className="container section">
        <Alert kind="error">{error || "Supplier profile unavailable."}</Alert>
      </div>
    );
  }

  const supplier = dashboard.supplier;
  const balance = dashboard.balance;
  const openOrders = orders.filter((order) =>
    ["awaiting_acceptance", "accepted", "ready", "in_transit"].includes(order.status),
  ).length;

  return (
    <div className="container portal-body">
      <PageHead
        eyebrow={`${supplier.code} · ${supplier.region}`}
        title={supplier.trading_name}
        description={`${supplier.legal_name} · rated ${supplier.rating.toFixed(1)} / 5 · commission ${percent(
          dashboard.config.commission_bp,
        )} on merchandise`}
        actions={
          <>
            <StatusBadge status={supplier.status} />
            <Link href="/shop" className="btn btn-secondary btn-sm">
              View the catalogue
            </Link>
          </>
        }
      />

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}

      <div style={{ marginBottom: 22 }}>
        <Tabs items={TABS} active={tab} onChange={setTab} />
      </div>

      {tab === "overview" ? (
        <div className="stack">
          <div className="stat-grid">
            <Stat label="Eligible for payout" value={money(balance.eligible)} hint={`After the ${dashboard.config.payout_hold_days}-day hold`} />
            <Stat label="In payout" value={money(balance.in_payout)} hint="Requested or approved" />
            <Stat label="Settled" value={money(balance.settled)} hint="Paid out to date" />
            <Stat label="Open orders" value={openOrders} hint="Awaiting action or in transit" />
          </div>

          <div className="split">
            <section className="card card-pad">
              <div className="spread" style={{ marginBottom: 12 }}>
                <h2 style={{ fontSize: "1.05rem" }}>Recent orders</h2>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => setTab("orders")}>
                  See all
                </button>
              </div>
              {dashboard.recent_orders.length === 0 ? (
                <p className="muted small">No orders yet. They appear here as soon as a customer pays.</p>
              ) : (
                <div className="stack-sm">
                  {dashboard.recent_orders.map((order) => (
                    <button
                      key={order.id}
                      type="button"
                      className="row-card"
                      style={{ textAlign: "left", cursor: "pointer", padding: "12px 14px" }}
                      onClick={() => {
                        setTab("orders");
                        setOrderFilter("all");
                      }}
                    >
                      <div className="spread">
                        <div>
                          <div className="row" style={{ gap: 8 }}>
                            <strong style={{ fontSize: ".92rem" }}>{order.code}</strong>
                            <StatusBadge status={order.status} />
                          </div>
                          <div className="small faint">
                            {order.order?.customer_name ?? "Customer"} ·{" "}
                            {order.order?.placed_at ? date(order.order.placed_at) : ""}
                          </div>
                        </div>
                        <div className="right small">
                          <div className="price" style={{ fontSize: ".92rem" }}>
                            {money(order.merchandise_total)}
                          </div>
                          <div className="faint">{titleCase(order.payout_status)}</div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </section>

            <div className="stack">
              <section className="card card-pad">
                <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>What you earn</h2>
                <div className="kv">
                  <div>
                    <span>Commission to Usiri</span>
                    <strong>{money(dashboard.summary.commission)}</strong>
                    <div className="small faint">Calculated on merchandise</div>
                  </div>
                  <div>
                    <span>Products</span>
                    <strong>{dashboard.summary.products}</strong>
                  </div>
                  <div>
                    <span>Payout hold</span>
                    <strong>{dashboard.config.payout_hold_days} days</strong>
                  </div>
                  <div>
                    <span>Awaiting hold</span>
                    <strong>{balance.orders_awaiting_hold}</strong>
                  </div>
                </div>
                <p className="small faint" style={{ marginTop: 14 }}>
                  Commission is calculated on merchandise only. Delivery fees collected from the
                  customer are not part of your payout.
                </p>
              </section>

              <section className="card card-pad">
                <h2 style={{ fontSize: "1.05rem", marginBottom: 12 }}>Orders by status</h2>
                <div className="stack-sm">
                  {Object.keys(dashboard.summary.by_status).length === 0 ? (
                    <p className="muted small">Nothing yet.</p>
                  ) : (
                    Object.entries(dashboard.summary.by_status).map(([status, entry]) => (
                      <div key={status} className="spread small">
                        <span>
                          <StatusBadge status={status} />
                        </span>
                        <span>
                          {entry.orders} order{entry.orders === 1 ? "" : "s"} · {money(entry.value)}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          </div>
        </div>
      ) : null}

      {tab === "orders" ? (
        <div className="stack">
          <div className="chip-row">
            {ORDER_FILTERS.map((status) => (
              <button
                key={status}
                type="button"
                className={`chip${orderFilter === status ? " active" : ""}`}
                onClick={() => setOrderFilter(status)}
              >
                {status === "all" ? "All" : titleCase(status)}
              </button>
            ))}
          </div>
          <SupplierOrdersPanel orders={orders} onChanged={reloadOrders} filter={orderFilter} />
        </div>
      ) : null}

      {tab === "messages" ? <ChatInbox audience="supplier" /> : null}

      {tab === "products" ? (
        <SupplierProductsPanel products={products} departments={departments} onChanged={reloadProducts} />
      ) : null}

      {tab === "payouts" ? (
        <div className="stack">
          <div className="stat-grid">
            <Stat label="Eligible now" value={money(balance.eligible)} />
            <Stat label="In payout" value={money(balance.in_payout)} />
            <Stat label="Settled" value={money(balance.settled)} />
          </div>
          {payouts.length === 0 ? (
            <p className="muted">
              No payouts yet. Usiri finance requests a payout once delivered orders clear the hold
              period and meet the minimum amount.
            </p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Created</th>
                    <th>Period</th>
                    <th className="right">Amount</th>
                    <th>Status</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  {payouts.map((payout) => (
                    <tr key={payout.id}>
                      <td>{date(payout.created_at)}</td>
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
                      <td className="small faint">{payout.provider_ref ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ) : null}

      {tab === "returns" ? (
        <div>
          {returns.length === 0 ? (
            <p className="muted">No returns have been raised against your orders.</p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Return</th>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th className="right">Refund</th>
                  </tr>
                </thead>
                <tbody>
                  {returns.map((entry) => (
                    <tr key={entry.id}>
                      <td>
                        <div style={{ fontWeight: 600 }}>{entry.code}</div>
                        <div className="small faint">
                          {entry.order_code ?? ""} · {date(entry.requested_at)}
                        </div>
                      </td>
                      <td>
                        {entry.item?.product_name ?? "Item"}
                        <div className="small faint">{entry.item?.variant_name ?? ""}</div>
                      </td>
                      <td>{entry.qty}</td>
                      <td className="small">{titleCase(entry.reason)}</td>
                      <td>
                        <StatusBadge status={entry.status} />
                      </td>
                      <td className="right">{entry.refund_amount ? money(entry.refund_amount) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="small faint" style={{ marginTop: 14 }}>
            Returns are reviewed by Usiri support. Approved returns are refunded to the customer and
            deducted from your payable, including the commission on the returned merchandise.
          </p>
        </div>
      ) : null}
    </div>
  );
}
