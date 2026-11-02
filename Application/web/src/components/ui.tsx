"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { initials, statusTone, swatch, titleCase, toneClass } from "@/lib/format";

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: "green" | "amber" | "red" | "blue" | "neutral" | "brand";
  children: ReactNode;
}) {
  return <span className={`badge ${toneClass(tone)}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: string | null | undefined }) {
  if (!status) return null;
  return (
    <span className={`badge ${toneClass(statusTone(status))}`}>
      <span className="dot" />
      {titleCase(status)}
    </span>
  );
}

export function Alert({
  kind = "info",
  children,
}: {
  kind?: "error" | "success" | "info" | "warn";
  children: ReactNode;
}) {
  return <div className={`alert alert-${kind}`}>{children}</div>;
}

export function Empty({
  title,
  children,
  action,
}: {
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <h3>{title}</h3>
      {children ? <p>{children}</p> : null}
      {action ? <div style={{ marginTop: 18 }}>{action}</div> : null}
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="loading">
      <span className="spinner" aria-hidden />
      <span>{label}</span>
    </div>
  );
}

export function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
}) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {hint ? <div className="stat-hint">{hint}</div> : null}
    </div>
  );
}

export function Tabs<T extends string>({
  items,
  active,
  onChange,
}: {
  items: { id: T; label: string }[];
  active: T;
  onChange: (id: T) => void;
}) {
  return (
    <div className="tabs" role="tablist">
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          role="tab"
          aria-selected={active === item.id}
          className={`tab${active === item.id ? " active" : ""}`}
          onClick={() => onChange(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

export function Thumb({ name }: { name: string }) {
  return (
    <div className="product-thumb" style={{ background: swatch(name) }}>
      <span>{initials(name)}</span>
    </div>
  );
}

export function SmallThumb({ name }: { name: string }) {
  return (
    <div className="thumb-sm" style={{ background: swatch(name) }} aria-hidden>
      {initials(name)}
    </div>
  );
}

export function PageHead({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="portal-head">
      <div>
        {eyebrow ? <div className="tiny faint" style={{ marginBottom: 8 }}>{eyebrow}</div> : null}
        <h1>{title}</h1>
        {description ? <p className="muted" style={{ marginTop: 8, maxWidth: "62ch" }}>{description}</p> : null}
      </div>
      {actions ? <div className="btn-row">{actions}</div> : null}
    </div>
  );
}

export function BackLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Link href={href} className="small muted" style={{ display: "inline-block", marginBottom: 14 }}>
      ← {children}
    </Link>
  );
}
