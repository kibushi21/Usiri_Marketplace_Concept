"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { Alert, Empty, Loading, PageHead, SmallThumb } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { money } from "@/lib/format";
import { CART_EVENT } from "@/lib/session";
import type { Cart } from "@/lib/types";

export default function CartPage() {
  return (
    <RequireAuth roles={["customer"]}>
      <CartView />
    </RequireAuth>
  );
}

function CartView() {
  const { token } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const applyCart = useCallback((next: Cart) => {
    setCart(next);
    window.dispatchEvent(new Event(CART_EVENT));
  }, []);

  useEffect(() => {
    let active = true;
    api<Cart>("/cart", { token })
      .then((data) => {
        if (active) setCart(data);
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
  }, [token]);

  async function setQty(itemId: string, qty: number) {
    setBusy(itemId);
    setError("");
    try {
      const next = await api<Cart>(`/cart/items/${itemId}`, { method: "PATCH", body: { qty } });
      applyCart(next);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function remove(itemId: string) {
    setBusy(itemId);
    setError("");
    try {
      const next = await api<Cart>(`/cart/items/${itemId}`, { method: "DELETE" });
      applyCart(next);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function clear() {
    setBusy("clear");
    setError("");
    try {
      const next = await api<Cart>("/cart", { method: "DELETE" });
      applyCart(next);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (loading) return <Loading label="Opening your cart…" />;
  if (!cart) return <div className="container section"><Alert kind="error">{error || "Cart unavailable"}</Alert></div>;
  if (cart.items.length === 0) {
    return (
      <div className="container section">
        <PageHead title="Your cart" description="Items you add from the catalogue appear here." />
        <Empty
          title="Your cart is empty"
          action={
            <Link href="/shop" className="btn btn-primary">
              Browse the marketplace
            </Link>
          }
        >
          Start with a department or search for something specific. Delivery is calculated per supplier
          shipment.
        </Empty>
      </div>
    );
  }

  return (
    <div className="container portal-body">
      <PageHead
        title="Your cart"
        description={`${cart.item_count} ${cart.item_count === 1 ? "item" : "items"} from ${
          cart.supplier_groups.length
        } ${cart.supplier_groups.length === 1 ? "supplier" : "suppliers"}.`}
        actions={
          <button type="button" className="btn btn-ghost btn-sm" onClick={clear} disabled={busy === "clear"}>
            Clear cart
          </button>
        }
      />

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}

      <div className="split">
        <div className="stack">
          <div className="card">
            {cart.items.map((item, index) => (
              <div
                key={item.id}
                style={{
                  padding: "16px 18px",
                  borderTop: index === 0 ? "none" : "1px solid var(--line)",
                  display: "flex",
                  gap: 14,
                  alignItems: "flex-start",
                }}
              >
                <SmallThumb name={item.product_name} />
                <div className="grow">
                  <div className="spread" style={{ alignItems: "flex-start" }}>
                    <div>
                      <Link href={`/product/${item.product_slug}`} className="product-name">
                        {item.product_name}
                      </Link>
                      <div className="product-meta">
                        {item.variant_name} · {item.supplier_name}
                      </div>
                      <div className="small faint" style={{ marginTop: 2 }}>
                        {money(item.unit_price)} each
                      </div>
                    </div>
                    <div className="right">
                      <div className="price">{money(item.line_total)}</div>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        style={{ marginTop: 4 }}
                        onClick={() => remove(item.id)}
                        disabled={busy === item.id}
                      >
                        Remove
                      </button>
                    </div>
                  </div>

                  {item.warnings.length > 0 ? (
                    <div style={{ marginTop: 10 }}>
                      <Alert kind="warn">{item.warnings.join(" · ")}</Alert>
                    </div>
                  ) : null}

                  <div className="row" style={{ gap: 4, marginTop: 12 }}>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setQty(item.id, Math.max(1, item.qty - 1))}
                      disabled={busy === item.id || item.qty <= 1}
                      aria-label="Decrease quantity"
                    >
                      −
                    </button>
                    <span style={{ minWidth: 32, textAlign: "center", fontWeight: 600 }}>{item.qty}</span>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setQty(item.id, item.qty + 1)}
                      disabled={busy === item.id || item.qty >= Math.min(item.available, 20)}
                      aria-label="Increase quantity"
                    >
                      +
                    </button>
                    <span className="small faint" style={{ marginLeft: 8 }}>
                      {item.available} available
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="card card-pad">
            <div className="tiny faint" style={{ marginBottom: 12 }}>
              Deliveries
            </div>
            <div className="stack-sm">
              {cart.supplier_groups.map((group) => (
                <div key={group.supplier_id} className="spread">
                  <div>
                    <strong style={{ fontSize: ".93rem" }}>{group.supplier_name}</strong>
                    <div className="small faint">
                      Merchandise {money(group.merchandise_total)}
                      {group.merchandise_total < cart.free_delivery_threshold
                        ? ` · add ${money(cart.free_delivery_threshold - group.merchandise_total)} for free delivery`
                        : ""}
                    </div>
                  </div>
                  {group.delivery_fee === 0 ? (
                    <span className="badge badge-green">Free delivery</span>
                  ) : (
                    <span className="small">{money(group.delivery_fee)}</span>
                  )}
                </div>
              ))}
            </div>
            <p className="small faint" style={{ marginTop: 14 }}>
              Each supplier ships separately. Delivery is charged per supplier shipment; the cart total
              includes all of them.
            </p>
          </div>
        </div>

        <aside className="card card-pad" style={{ position: "sticky", top: 88 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>Order summary</h2>
          <div className="summary-line">
            <span className="muted">Subtotal</span>
            <span>{money(cart.subtotal)}</span>
          </div>
          <div className="summary-line">
            <span className="muted">Delivery ({cart.supplier_groups.length})</span>
            <span>{cart.delivery_total === 0 ? "Free" : money(cart.delivery_total)}</span>
          </div>
          <div className="summary-total">
            <span>Total</span>
            <span>{money(cart.total)}</span>
          </div>

          {cart.has_warnings ? (
            <div style={{ marginTop: 14 }}>
              <Alert kind="warn">
                Some items need attention before checkout. Adjust or remove the highlighted lines.
              </Alert>
            </div>
          ) : null}

          <Link
            href="/checkout"
            className="btn btn-primary btn-block"
            style={{ marginTop: 18, pointerEvents: cart.has_warnings ? "none" : undefined, opacity: cart.has_warnings ? 0.55 : 1 }}
            aria-disabled={cart.has_warnings}
          >
            Continue to checkout
          </Link>
          <Link href="/shop" className="btn btn-ghost btn-block btn-sm" style={{ marginTop: 6 }}>
            Keep shopping
          </Link>

          <p className="small faint" style={{ marginTop: 16 }}>
            Stock is reserved when you start payment and held for a short window. Prices and delivery
            are recalculated at checkout.
          </p>
        </aside>
      </div>
    </div>
  );
}
