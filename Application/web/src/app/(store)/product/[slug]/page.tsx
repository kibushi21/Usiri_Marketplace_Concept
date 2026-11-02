"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Alert, BackLink, Loading, Thumb } from "@/components/ui";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { money, titleCase } from "@/lib/format";
import { CART_EVENT } from "@/lib/session";
import type { Cart, ProductDetail } from "@/lib/types";

export default function ProductPage() {
  const params = useParams<{ slug: string }>();
  const router = useRouter();
  const { user } = useAuth();

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [variantId, setVariantId] = useState("");
  const [qty, setQty] = useState(1);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    api<ProductDetail>(`/catalogue/products/${params.slug}`, { auth: false })
      .then((data) => {
        if (!active) return;
        setProduct(data);
        const firstAvailable = data.variants.find((variant) => variant.available > 0) ?? data.variants[0];
        setVariantId(firstAvailable?.id ?? "");
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
  }, [params.slug]);

  const variant = product?.variants.find((entry) => entry.id === variantId);

  async function addToCart() {
    if (!variant) return;
    if (!user) {
      router.push(`/login?next=${encodeURIComponent(`/product/${params.slug}`)}`);
      return;
    }
    if (user.role !== "customer") {
      setError("Only customer accounts can shop. Sign in with a customer account.");
      return;
    }
    setAdding(true);
    setError("");
    setNotice("");
    try {
      await api<Cart>("/cart/items", {
        method: "POST",
        body: { variant_id: variant.id, qty },
      });
      window.dispatchEvent(new Event(CART_EVENT));
      setNotice(`${qty} × ${variant.name} added to your cart.`);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setAdding(false);
    }
  }

  if (loading) return <div className="container"><Loading label="Loading product…" /></div>;
  if (!product) {
    return (
      <div className="container section">
        <Alert kind="error">{error || "Product not found."}</Alert>
        <p style={{ marginTop: 16 }}>
          <Link href="/shop" className="btn btn-secondary">
            Back to the shop
          </Link>
        </p>
      </div>
    );
  }

  const maxQty = Math.min(variant?.available ?? 0, 20);
  const attributes = product.attributes ?? {};

  return (
    <div className="container" style={{ paddingBottom: 40 }}>
      <div style={{ paddingTop: 26 }}>
        <BackLink href="/shop">Back to the catalogue</BackLink>
      </div>

      <div className="split">
        <div className="stack">
          <div className="card" style={{ overflow: "hidden", borderRadius: 18 }}>
            <Thumb name={product.name} />
          </div>
          <div className="card card-pad">
            <h2 style={{ fontSize: "1.1rem", marginBottom: 10 }}>About this product</h2>
            <p className="muted" style={{ whiteSpace: "pre-line" }}>
              {product.description || "No description supplied yet."}
            </p>
            {Object.keys(attributes).length > 0 ? (
              <div className="kv" style={{ marginTop: 20 }}>
                {Object.entries(attributes).map(([key, value]) => (
                  <div key={key}>
                    <span>{titleCase(key)}</span>
                    <strong>{String(value)}</strong>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="stack">
          <div className="card card-pad-lg">
            <div className="row-wrap" style={{ gap: 8 }}>
              <span className="tiny faint">
                {product.department_name ?? titleCase(product.department_slug ?? "")}
              </span>
              {product.brand ? <span className="tiny faint">· {product.brand}</span> : null}
            </div>
            <h1 style={{ fontFamily: "var(--font-serif)", fontWeight: 500, fontSize: "1.9rem", margin: "10px 0 6px" }}>
              {product.name}
            </h1>
            <p className="muted small">
              Sold by {product.supplier} · {product.supplier_region} · ★ {product.supplier_rating.toFixed(1)}
            </p>

            <div className="price" style={{ margin: "18px 0 6px", fontSize: "1.6rem" }}>
              {variant ? money(variant.price) : money(product.price_from)}
            </div>
            <p className="small faint">
              {variant
                ? variant.available > 0
                  ? `${variant.available} in stock`
                  : "Out of stock"
                : "Choose an option"}
            </p>

            {product.variants.length > 1 ? (
              <div style={{ marginTop: 18 }}>
                <div className="small muted" style={{ marginBottom: 8, fontWeight: 600 }}>
                  Option
                </div>
                <div className="chip-row">
                  {product.variants.map((entry) => (
                    <button
                      key={entry.id}
                      type="button"
                      className={`chip${entry.id === variantId ? " active" : ""}`}
                      onClick={() => {
                        setVariantId(entry.id);
                        setQty(1);
                        setNotice("");
                      }}
                      disabled={entry.available === 0}
                    >
                      {entry.name}
                      {entry.available === 0 ? " · sold out" : ""}
                    </button>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="row" style={{ marginTop: 22, gap: 14 }}>
              <div className="row" style={{ gap: 4 }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setQty((value) => Math.max(1, value - 1))}
                  disabled={qty <= 1}
                  aria-label="Decrease quantity"
                >
                  −
                </button>
                <span style={{ minWidth: 34, textAlign: "center", fontWeight: 600 }}>{qty}</span>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setQty((value) => Math.min(maxQty || 1, value + 1))}
                  disabled={qty >= maxQty}
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>
              <button
                type="button"
                className="btn btn-primary grow"
                onClick={addToCart}
                disabled={adding || !variant || variant.available === 0}
              >
                {adding ? "Adding…" : "Add to cart"}
              </button>
            </div>

            {error ? <div style={{ marginTop: 14 }}><Alert kind="error">{error}</Alert></div> : null}
            {notice ? (
              <div style={{ marginTop: 14 }}>
                <Alert kind="success">
                  {notice}{" "}
                  <Link href="/cart" style={{ fontWeight: 600, textDecoration: "underline" }}>
                    Go to cart
                  </Link>
                </Alert>
              </div>
            ) : null}

            <hr className="divider" />
            <div className="stack-sm small muted">
              <span>Delivery is arranged per supplier shipment and shown in your cart.</span>
              <span>Returns accepted within the published window after delivery.</span>
              <span>Payment is taken by the authorised payment provider, not stored by Usiri.</span>
            </div>
          </div>

          <div className="card card-pad">
            <div className="spread">
              <div>
                <div className="tiny faint">Supplier</div>
                <strong>{product.supplier}</strong>
                <div className="small muted">{product.supplier_region}, Tanzania</div>
              </div>
              <span className="badge badge-brand">Verified</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
