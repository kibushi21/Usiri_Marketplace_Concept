"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { RequireAuth } from "@/components/require-auth";
import { Alert, Empty, Loading, PageHead, SmallThumb } from "@/components/ui";
import { api, idempotencyKey } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { money } from "@/lib/format";
import { CART_EVENT } from "@/lib/session";
import type { CheckoutQuote, Order, Payment } from "@/lib/types";

interface CheckoutResponse {
  order: Order;
  payment_required: boolean;
  reservation_expires_in_minutes: number;
}

interface PaymentResponse {
  payment: Payment;
  order: Order;
}

const METHODS = [
  { id: "mobile_money", label: "Mobile money", hint: "M-Pesa, Tigo Pesa, Airtel Money" },
  { id: "card", label: "Card", hint: "Visa or Mastercard via the PSP" },
  { id: "bank", label: "Bank transfer", hint: "Works with bank redirect providers" },
];

const EMPTY_ADDRESS = {
  recipient_name: "",
  phone: "",
  region: "",
  district: "",
  ward: "",
  street: "",
  landmark: "",
  label: "Delivery",
};

export default function CheckoutPage() {
  return (
    <RequireAuth roles={["customer"]}>
      <CheckoutView />
    </RequireAuth>
  );
}

function CheckoutView() {
  const { addresses, user, refresh } = useAuth();
  const router = useRouter();

  const [quote, setQuote] = useState<CheckoutQuote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [placing, setPlacing] = useState(false);

  const [addressId, setAddressId] = useState("");
  const [form, setForm] = useState(EMPTY_ADDRESS);
  const [notes, setNotes] = useState("");
  const [method, setMethod] = useState("mobile_money");
  const [msisdn, setMsisdn] = useState(user?.phone ?? "");

  useEffect(() => {
    if (addresses.length > 0) {
      const preferred = addresses.find((entry) => entry.is_default) ?? addresses[0];
      setAddressId(preferred.id);
    }
  }, [addresses]);

  useEffect(() => {
    let active = true;
    api<CheckoutQuote>("/checkout/quote", { method: "POST" })
      .then((data) => {
        if (active) setQuote(data);
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

  function update(field: keyof typeof EMPTY_ADDRESS, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function placeOrder() {
    if (!quote || !quote.can_checkout) return;
    setPlacing(true);
    setError("");

    const addressPayload =
      addressId && addressId !== "new"
        ? { address_id: addressId }
        : {
            ...form,
            recipient_name: form.recipient_name.trim(),
            phone: form.phone.trim(),
            region: form.region.trim(),
            district: form.district.trim(),
            street: form.street.trim(),
          };

    try {
      const checkout = await api<CheckoutResponse>("/checkout", {
        method: "POST",
        body: { ...addressPayload, notes: notes || null },
        headers: { "Idempotency-Key": idempotencyKey() },
      });
      const paid = await api<PaymentResponse>(`/orders/${checkout.order.id}/payments`, {
        method: "POST",
        body: { method, msisdn: method === "mobile_money" ? msisdn.trim() || null : null },
        headers: { "Idempotency-Key": idempotencyKey() },
      });
      window.dispatchEvent(new Event(CART_EVENT));
      void refresh();
      router.push(`/pay/${paid.payment.id}`);
    } catch (cause) {
      setError((cause as Error).message);
      setPlacing(false);
    }
  }

  if (loading) return <Loading label="Reviewing your basket…" />;
  if (!quote) {
    return (
      <div className="container section">
        <Alert kind="error">{error || "Could not load the checkout."}</Alert>
      </div>
    );
  }

  if (quote.items.length === 0) {
    return (
      <div className="container section">
        <Empty
          title="Nothing to check out"
          action={
            <Link href="/shop" className="btn btn-primary">
              Browse the marketplace
            </Link>
          }
        >
          Your cart is empty, so there is nothing to pay for yet.
        </Empty>
      </div>
    );
  }

  const usingNewAddress = addressId === "new" || addresses.length === 0;

  return (
    <div className="container portal-body">
      <PageHead
        title="Checkout"
        description="Confirm where this goes and how you want to pay. Stock is reserved once payment starts."
      />

      {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}
      {!quote.can_checkout ? (
        <div style={{ marginBottom: 16 }}>
          <Alert kind="warn">
            {quote.issues.join(" · ")}
            {" "}
            <Link href="/cart" style={{ fontWeight: 600, textDecoration: "underline" }}>
              Return to cart
            </Link>
          </Alert>
        </div>
      ) : null}

      <div className="split">
        <div className="stack">
          <section className="card card-pad">
            <div className="spread" style={{ marginBottom: 14 }}>
              <h2 style={{ fontSize: "1.05rem" }}>Delivery address</h2>
              <span className="small faint">{addresses.length} saved</span>
            </div>

            {addresses.length > 0 ? (
              <div className="stack-sm" style={{ marginBottom: 16 }}>
                {addresses.map((address) => (
                  <label
                    key={address.id}
                    className="row-card"
                    style={{
                      display: "flex",
                      gap: 12,
                      alignItems: "flex-start",
                      cursor: "pointer",
                      borderColor: addressId === address.id ? "var(--brand)" : undefined,
                      background: addressId === address.id ? "var(--brand-soft)" : undefined,
                    }}
                  >
                    <input
                      type="radio"
                      name="address"
                      checked={addressId === address.id}
                      onChange={() => setAddressId(address.id)}
                      style={{ width: 16, height: 16, marginTop: 4, accentColor: "var(--brand)" }}
                    />
                    <div>
                      <strong style={{ fontSize: ".94rem" }}>
                        {address.label}
                        {address.is_default ? " · default" : ""}
                      </strong>
                      <div className="small muted">
                        {address.recipient_name} · {address.phone}
                      </div>
                      <div className="small muted">
                        {[address.street, address.ward, address.district, address.region]
                          .filter(Boolean)
                          .join(", ")}
                      </div>
                    </div>
                  </label>
                ))}
                <label className="row-card" style={{ display: "flex", gap: 12, alignItems: "center", cursor: "pointer" }}>
                  <input
                    type="radio"
                    name="address"
                    checked={addressId === "new"}
                    onChange={() => setAddressId("new")}
                    style={{ width: 16, height: 16, accentColor: "var(--brand)" }}
                  />
                  <span style={{ fontSize: ".94rem" }}>Deliver to a different address</span>
                </label>
              </div>
            ) : null}

            {usingNewAddress ? (
              <div className="form-grid">
                <label className="field">
                  <span>Recipient name</span>
                  <input
                    value={form.recipient_name}
                    onChange={(event) => update("recipient_name", event.target.value)}
                    placeholder="Full name"
                    autoComplete="name"
                  />
                </label>
                <label className="field">
                  <span>Phone</span>
                  <input
                    value={form.phone}
                    onChange={(event) => update("phone", event.target.value)}
                    placeholder="+255 7xx xxx xxx"
                    autoComplete="tel"
                  />
                </label>
                <label className="field">
                  <span>Region</span>
                  <input
                    value={form.region}
                    onChange={(event) => update("region", event.target.value)}
                    placeholder="Dar es Salaam"
                  />
                </label>
                <label className="field">
                  <span>District</span>
                  <input
                    value={form.district}
                    onChange={(event) => update("district", event.target.value)}
                    placeholder="Kinondoni"
                  />
                </label>
                <label className="field">
                  <span>Ward</span>
                  <input
                    value={form.ward}
                    onChange={(event) => update("ward", event.target.value)}
                    placeholder="Mikocheni"
                  />
                </label>
                <label className="field">
                  <span>Leaflet / label</span>
                  <input
                    value={form.label}
                    onChange={(event) => update("label", event.target.value)}
                    placeholder="Home, office…"
                  />
                </label>
                <label className="field span-2">
                  <span>Street</span>
                  <input
                    value={form.street}
                    onChange={(event) => update("street", event.target.value)}
                    placeholder="Street, house number"
                  />
                </label>
                <label className="field span-2">
                  <span>Landmark (optional)</span>
                  <input
                    value={form.landmark}
                    onChange={(event) => update("landmark", event.target.value)}
                    placeholder="Nearest landmark"
                  />
                </label>
              </div>
            ) : null}

            <label className="field" style={{ marginTop: 16 }}>
              <span>Order notes (optional)</span>
              <textarea
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
                placeholder="Anything the supplier or carrier should know"
              />
            </label>
          </section>

          <section className="card card-pad">
            <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>Payment method</h2>
            <div className="stack-sm">
              {METHODS.map((option) => (
                <label
                  key={option.id}
                  className="row-card"
                  style={{
                    display: "flex",
                    gap: 12,
                    alignItems: "center",
                    cursor: "pointer",
                    borderColor: method === option.id ? "var(--brand)" : undefined,
                    background: method === option.id ? "var(--brand-soft)" : undefined,
                  }}
                >
                  <input
                    type="radio"
                    name="method"
                    checked={method === option.id}
                    onChange={() => setMethod(option.id)}
                    style={{ width: 16, height: 16, accentColor: "var(--brand)" }}
                  />
                  <div>
                    <strong style={{ fontSize: ".94rem" }}>{option.label}</strong>
                    <div className="small muted">{option.hint}</div>
                  </div>
                </label>
              ))}
            </div>
            {method === "mobile_money" ? (
              <label className="field" style={{ marginTop: 14 }}>
                <span>Mobile money number</span>
                <input
                  value={msisdn}
                  onChange={(event) => setMsisdn(event.target.value)}
                  placeholder="+255 7xx xxx xxx"
                  autoComplete="tel"
                />
              </label>
            ) : null}
            <p className="small faint" style={{ marginTop: 14 }}>
              In this demo, the payment provider is a sandbox. You will approve or decline the payment
              on the next screen; no money moves.
            </p>
          </section>
        </div>

        <aside className="card card-pad" style={{ position: "sticky", top: 88 }}>
          <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>Order summary</h2>
          <div className="stack-sm" style={{ marginBottom: 14 }}>
            {quote.items.map((item) => (
              <div key={item.id} className="row" style={{ alignItems: "flex-start" }}>
                <SmallThumb name={item.product_name} />
                <div className="grow">
                  <div style={{ fontSize: ".9rem", fontWeight: 600 }}>
                    {item.qty} × {item.product_name}
                  </div>
                  <div className="small faint">
                    {item.variant_name} · {item.supplier_name}
                  </div>
                </div>
                <div className="small">{money(item.line_total)}</div>
              </div>
            ))}
          </div>

          <div className="summary-line">
            <span className="muted">Subtotal</span>
            <span>{money(quote.subtotal)}</span>
          </div>
          {quote.supplier_groups.map((group) => (
            <div key={group.supplier_id} className="summary-line small">
              <span className="faint">{group.supplier_name} delivery</span>
              <span>{group.delivery_fee === 0 ? "Free" : money(group.delivery_fee)}</span>
            </div>
          ))}
          <div className="summary-total">
            <span>Total due</span>
            <span>{money(quote.total)}</span>
          </div>

          <button
            type="button"
            className="btn btn-primary btn-block"
            style={{ marginTop: 18 }}
            onClick={placeOrder}
            disabled={placing || !quote.can_checkout}
          >
            {placing ? "Creating your order…" : `Place order · ${money(quote.total)}`}
          </button>
          <Link href="/cart" className="btn btn-ghost btn-block btn-sm" style={{ marginTop: 6 }}>
            Back to cart
          </Link>
          <p className="small faint" style={{ marginTop: 16 }}>
            By placing the order you confirm the delivery details above. The reservation is held for a
            short window while payment completes.
          </p>
        </aside>
      </div>
    </div>
  );
}
