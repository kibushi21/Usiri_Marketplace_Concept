"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Alert, Loading, StatusBadge } from "@/components/ui";
import { api, idempotencyKey } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { money } from "@/lib/format";
import type { Order, Payment } from "@/lib/types";

interface PaymentView {
  payment: Payment;
  order: Order;
}

const METHOD_LABEL: Record<string, string> = {
  mobile_money: "Mobile money",
  card: "Card",
  bank: "Bank transfer",
};

export default function PayPage() {
  const params = useParams<{ paymentId: string }>();
  const router = useRouter();
  const { user, ready } = useAuth();

  const [view, setView] = useState<PaymentView | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (ready && !user) router.replace(`/login?next=${encodeURIComponent(`/pay/${params.paymentId}`)}`);
  }, [ready, user, params.paymentId, router]);

  useEffect(() => {
    if (!user) return;
    let active = true;
    api<PaymentView>(`/payments/${params.paymentId}`)
      .then((data) => {
        if (active) setView(data);
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
  }, [user, params.paymentId]);

  async function simulate(outcome: "succeeded" | "failed") {
    setBusy(outcome);
    setError("");
    try {
      const data = await api<PaymentView>(`/payments/${params.paymentId}/simulate`, {
        method: "POST",
        body: { outcome },
      });
      setView(data);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  async function retryPayment() {
    if (!view) return;
    setBusy("retry");
    setError("");
    try {
      const data = await api<PaymentView>(`/orders/${view.order.id}/payments`, {
        method: "POST",
        body: { method: view.payment.method, msisdn: view.payment.msisdn },
        headers: { "Idempotency-Key": idempotencyKey() },
      });
      router.replace(`/pay/${data.payment.id}`);
    } catch (cause) {
      setError((cause as Error).message);
      setBusy("");
    }
  }

  if (!ready || loading) return <div className="pay-shell"><Loading label="Loading the payment…" /></div>;

  if (!view) {
    return (
      <div className="pay-shell">
        <div className="pay-card">
          <Alert kind="error">{error || "Payment not found."}</Alert>
          <Link href="/orders" className="btn btn-secondary btn-block" style={{ marginTop: 18 }}>
            Back to orders
          </Link>
        </div>
      </div>
    );
  }

  const { payment, order } = view;
  const pending = payment.status === "pending" || payment.status === "initiated";

  return (
    <div className="pay-shell">
      <div className="pay-card">
        <div className="pay-brand">
          <span>Usiri · checkout</span>
          <span>Sandbox PSP</span>
        </div>

        <div style={{ marginTop: 26 }}>
          {payment.status === "succeeded" ? (
            <>
              <div className="pay-ring ok">✓</div>
              <h1 className="serif" style={{ fontSize: "1.6rem", fontWeight: 500 }}>
                Payment received
              </h1>
              <div className="pay-amount">{money(payment.amount)}</div>
              <p className="small muted">
                Confirmed against order {order.code}. The supplier has been notified and will accept
                the order next.
              </p>
            </>
          ) : payment.status === "failed" ? (
            <>
              <div className="pay-ring bad">!</div>
              <h1 className="serif" style={{ fontSize: "1.6rem", fontWeight: 500 }}>
                Payment declined
              </h1>
              <div className="pay-amount">{money(payment.amount)}</div>
              <p className="small muted">
                {payment.failure_reason ?? "The provider declined the payment."} Your stock reservation
                is still held until it expires, so you can try again now.
              </p>
            </>
          ) : payment.status === "succeeded_unmatched" ? (
            <>
              <div className="pay-ring bad">!</div>
              <h1 className="serif" style={{ fontSize: "1.6rem", fontWeight: 500 }}>
                Needs reconciliation
              </h1>
              <p className="small muted">{payment.failure_reason}</p>
            </>
          ) : (
            <>
              <div className="pay-ring">₮</div>
              <h1 className="serif" style={{ fontSize: "1.6rem", fontWeight: 500 }}>
                Approve the payment
              </h1>
              <div className="pay-amount">{money(payment.amount)}</div>
              <p className="small muted">
                {METHOD_LABEL[payment.method] ?? payment.method}
                {payment.msisdn ? ` · ${payment.msisdn}` : ""}
              </p>
            </>
          )}
        </div>

        <hr className="divider" />

        <div className="stack-sm small">
          <div className="spread">
            <span className="faint">Order</span>
            <strong>{order.code}</strong>
          </div>
          <div className="spread">
            <span className="faint">Payment status</span>
            <StatusBadge status={payment.status} />
          </div>
          <div className="spread">
            <span className="faint">Provider reference</span>
            <span style={{ fontFamily: "ui-monospace, monospace", fontSize: ".8rem" }}>
              {payment.provider_ref ?? "—"}
            </span>
          </div>
          <div className="spread">
            <span className="faint">Delivery to</span>
            <span className="right">
              {order.delivery_address.recipient_name} · {order.delivery_address.region}
            </span>
          </div>
        </div>

        {error ? <div style={{ marginTop: 16 }}><Alert kind="error">{error}</Alert></div> : null}

        <div style={{ marginTop: 22 }} className="stack-sm">
          {pending ? (
            <>
              <button
                type="button"
                className="btn btn-primary btn-block"
                onClick={() => simulate("succeeded")}
                disabled={busy !== ""}
              >
                {busy === "succeeded" ? "Processing…" : `Pay ${money(payment.amount)}`}
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-block"
                onClick={() => simulate("failed")}
                disabled={busy !== ""}
              >
                {busy === "failed" ? "Declining…" : "Decline the payment"}
              </button>
            </>
          ) : null}

          {payment.status === "succeeded" ? (
            <Link href={`/orders/${order.id}`} className="btn btn-primary btn-block">
              View the order
            </Link>
          ) : null}

          {payment.status === "failed" ? (
            <>
              <button
                type="button"
                className="btn btn-primary btn-block"
                onClick={retryPayment}
                disabled={busy !== ""}
              >
                {busy === "retry" ? "Starting a new payment…" : "Try again"}
              </button>
              <Link href={`/orders/${order.id}`} className="btn btn-secondary btn-block">
                Back to the order
              </Link>
            </>
          ) : null}

          {payment.status === "succeeded_unmatched" ? (
            <Link href="/support" className="btn btn-secondary btn-block">
              Contact support
            </Link>
          ) : null}
        </div>

        <p className="small faint" style={{ marginTop: 20, textAlign: "center" }}>
          Demo sandbox · no real funds move. Card and mobile money are represented by the same mock
          provider.
        </p>
      </div>
    </div>
  );
}
