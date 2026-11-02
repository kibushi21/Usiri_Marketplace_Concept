"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Alert, Loading } from "@/components/ui";
import { homeForRole, useAuth } from "@/lib/auth";

const DEMO_PASSWORD = "Usiri#2026";

const DEMO_GROUPS: { label: string; accounts: { email: string; who: string }[] }[] = [
  {
    label: "Customer",
    accounts: [
      { email: "demo@usiri.co.tz", who: "Asha Juma" },
      { email: "daniel@example.co.tz", who: "Daniel Kimaro" },
    ],
  },
  {
    label: "Supplier",
    accounts: [
      { email: "mwanga@suppliers.usiri.co.tz", who: "Mwanga Appliances" },
      { email: "sanaa@suppliers.usiri.co.tz", who: "Sanaa Fashion House" },
      { email: "kariakoo@suppliers.usiri.co.tz", who: "Kariakoo Homeware" },
    ],
  },
  {
    label: "Operations",
    accounts: [
      { email: "ops@usiri.co.tz", who: "Ops admin" },
      { email: "finance@usiri.co.tz", who: "Finance · maker" },
      { email: "finance2@usiri.co.tz", who: "Finance · checker" },
      { email: "support@usiri.co.tz", who: "Support" },
      { email: "admin@usiri.co.tz", who: "Superadmin" },
    ],
  },
];

export default function LoginPage() {
  const { user, ready, login, logout } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [next, setNext] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const target = params.get("next");
    if (target && target.startsWith("/")) setNext(target);
  }, []);

  async function submit(loginEmail: string, loginPassword: string) {
    setBusy(loginEmail);
    setError("");
    try {
      const account = await login(loginEmail, loginPassword);
      router.push(next || homeForRole(account.role));
    } catch (cause) {
      setError((cause as Error).message);
      setBusy("");
    }
  }

  if (!ready) return <Loading label="Checking your session…" />;

  if (user) {
    return (
      <div className="auth-wrap">
        <div className="auth-card">
          <h1>You are signed in</h1>
          <p className="muted" style={{ marginTop: 6 }}>
            {user.full_name} · {user.email}
          </p>
          <div className="stack-sm" style={{ marginTop: 22 }}>
            <Link href={next || homeForRole(user.role)} className="btn btn-primary btn-block">
              Continue
            </Link>
            <Link href="/" className="btn btn-secondary btn-block">
              Back to the marketplace
            </Link>
            <button type="button" className="btn btn-ghost btn-block" onClick={logout}>
              Sign out
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Welcome back</h1>
        <p className="muted small" style={{ marginBottom: 22 }}>
          One account for shopping, selling and operations — your role decides what you see.
        </p>

        {error ? <div style={{ marginBottom: 16 }}><Alert kind="error">{error}</Alert></div> : null}

        <form
          className="stack"
          onSubmit={(event) => {
            event.preventDefault();
            void submit(email.trim(), password);
          }}
        >
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <button type="submit" className="btn btn-primary btn-block" disabled={busy !== ""}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="auth-alt">
          New here? <Link href="/register">Create a customer account</Link>
        </p>

        <div className="demo-box">
          <strong style={{ color: "var(--ink)" }}>Demo accounts</strong>
          <div className="small" style={{ marginTop: 4 }}>
            Password for every account: <code>{DEMO_PASSWORD}</code>
          </div>
          {DEMO_GROUPS.map((group) => (
            <div key={group.label} style={{ marginTop: 10 }}>
              <div className="tiny faint">{group.label}</div>
              <div className="demo-grid">
                {group.accounts.map((account) => (
                  <button
                    key={account.email}
                    type="button"
                    onClick={() => {
                      setEmail(account.email);
                      setPassword(DEMO_PASSWORD);
                      void submit(account.email, DEMO_PASSWORD);
                    }}
                    disabled={busy !== ""}
                  >
                    {account.who}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
