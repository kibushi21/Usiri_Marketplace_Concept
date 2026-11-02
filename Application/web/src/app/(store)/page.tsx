"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ProductCard } from "@/components/product-card";
import { Alert, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import { money } from "@/lib/format";
import type { Department, Meta, ProductPage } from "@/lib/types";

export default function HomePage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [products, setProducts] = useState<ProductPage | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      api<Department[]>("/catalogue/departments", { auth: false }),
      api<ProductPage>("/catalogue/products?limit=8&sort=featured", { auth: false }),
      api<Meta>("/meta", { auth: false }),
    ])
      .then(([departmentList, productList, metaInfo]) => {
        if (!active) return;
        setDepartments(departmentList);
        setProducts(productList);
        setMeta(metaInfo);
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

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <span className="eyebrow">
              <span className="dot" style={{ background: "var(--brand)" }} />
              Managed marketplace · Tanzania
            </span>
            <h1>
              Everything for the home,
              <br />
              from suppliers you can <em>trace</em>.
            </h1>
            <p className="lede">
              Six departments, one checkout. Verified Tanzanian suppliers hold the stock, licensed
              carriers deliver it, and Usiri stays answerable for the whole order — including the
              awkward parts.
            </p>
            <div className="hero-actions">
              <Link href="/shop" className="btn btn-primary">
                Shop the marketplace
              </Link>
              <a href="#how" className="btn btn-secondary">
                How an order works
              </a>
            </div>
            <p className="small faint" style={{ marginTop: 20 }}>
              Prices in TZS · Delivery arranged per supplier · 7-day returns on delivered items
            </p>
          </div>

          <aside className="hero-card">
            <div>
              <div className="tiny" style={{ color: "rgba(246,239,223,.7)", marginBottom: 10 }}>
                The promise
              </div>
              <h3>One order, however many suppliers it takes.</h3>
              <p style={{ color: "rgba(246,239,223,.78)", fontSize: ".92rem" }}>
                We split your basket behind the scenes, keep one payment and one support thread, and
                tell you exactly which shipment is where.
              </p>
            </div>
            <div className="hero-stat">
              <div>
                <strong>{departments.length || 6}</strong>
                <span>Departments</span>
              </div>
              <div>
                <strong>{meta ? money(meta.delivery_fee_flat) : "TSh 7,000"}</strong>
                <span>Delivery per supplier</span>
              </div>
              <div>
                <strong>{meta ? money(meta.free_delivery_threshold) : "TSh 150,000"}</strong>
                <span>Free delivery over</span>
              </div>
            </div>
          </aside>
        </div>
      </section>

      {error ? (
        <div className="container">
          <Alert kind="error">{error}</Alert>
        </div>
      ) : null}

      <section className="section">
        <div className="container">
          <div className="section-head">
            <div>
              <h2 className="section-title">Shop by department</h2>
              <p className="muted small">Six bounded departments. Nothing endless.</p>
            </div>
            <Link href="/shop" className="btn btn-ghost btn-sm">
              View all products →
            </Link>
          </div>

          {loading ? (
            <Loading label="Loading departments…" />
          ) : (
            <div className="dept-grid">
              {departments.map((department) => (
                <Link
                  key={department.id}
                  href={`/shop?department=${department.slug}`}
                  className="dept-card"
                >
                  <span className="tiny faint">{department.name_sw}</span>
                  <strong>{department.name}</strong>
                  <span className="count">
                    {department.product_count} {department.product_count === 1 ? "product" : "products"}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head">
            <div>
              <h2 className="section-title">New on the shelves</h2>
              <p className="muted small">Added by verified suppliers, priced in TZS.</p>
            </div>
          </div>
          {loading ? (
            <Loading label="Loading products…" />
          ) : products && products.items.length > 0 ? (
            <div className="product-grid">
              {products.items.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <p className="muted">The catalogue is empty. Run the seed command to load demo data.</p>
          )}
        </div>
      </section>

      <section className="section" id="how">
        <div className="container">
          <div className="section-head">
            <div>
              <h2 className="section-title">How an order works</h2>
              <p className="muted small">
                Managed means someone is accountable at every hand-off, not just at checkout.
              </p>
            </div>
          </div>
          <div className="steps">
            <article className="step">
              <h4>Pick across suppliers</h4>
              <p>
                Your basket can hold items from several suppliers. Delivery is calculated per
                supplier shipment and free above the basket threshold.
              </p>
            </article>
            <article className="step">
              <h4>Pay once</h4>
              <p>
                Payment goes through an authorised provider. Stock is reserved while you pay and
                committed when the provider confirms capture.
              </p>
            </article>
            <article className="step">
              <h4>Track each shipment</h4>
              <p>
                Suppliers accept, prepare and hand to a licensed carrier. Every shipment has its own
                status and reference, shown against the order.
              </p>
            </article>
            <article className="step">
              <h4>Return within 7 days</h4>
              <p>
                Delivered items can be returned inside the window. Approved returns are refunded
                through the original payment provider.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="band">
            <div className="split" style={{ alignItems: "center" }}>
              <div>
                <h2>Sell with Usiri, without building a storefront.</h2>
                <p>
                  Suppliers keep their own stock and prices. We bring the customers, coordinate
                  delivery and settle payouts after the payout hold — configured by the operations
                  team, not hard-coded into the marketplace.
                </p>
              </div>
              <div className="stack-sm">
                <Link href="/login" className="btn btn-primary">
                  Open the supplier portal
                </Link>
                <span className="small" style={{ color: "rgba(244,236,219,.7)" }}>
                  Demo accounts are listed on the sign-in page.
                </span>
              </div>
            </div>
            <div className="band-grid">
              <div className="band-item">
                <strong>Commission per supplier</strong>
                <span>Set in basis points, overridable per supplier.</span>
              </div>
              <div className="band-item">
                <strong>Payout hold</strong>
                <span>Balances become eligible after delivery plus the hold window.</span>
              </div>
              <div className="band-item">
                <strong>Maker-checker payouts</strong>
                <span>One person requests, a different person approves.</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {meta ? (
        <section className="section" style={{ paddingTop: 0 }}>
          <div className="container">
            <div className="row-wrap small muted" style={{ justifyContent: "space-between" }}>
              <span>
                Returns window: {meta.return_window_days} days after delivery · Reservations hold
                stock for {meta.reservation_ttl_minutes} minutes
              </span>
              <span>
                Support: {meta.support_email} · {meta.support_phone}
              </span>
            </div>
          </div>
        </section>
      ) : null}
    </>
  );
}
