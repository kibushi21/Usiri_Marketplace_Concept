"use client";

import { useState } from "react";

import { api } from "@/lib/api";
import type { Shipment } from "@/lib/types";

const OVERRIDE_STATUSES = [
  "picked_up",
  "in_transit",
  "out_for_delivery",
  "delayed",
  "delivery_attempted",
  "returned_to_sender",
];

const CLOSED_STATUSES = ["delivered", "cancelled", "returned_to_sender"];

export function ShipmentTrackingForm({
  shipment,
  onUpdated,
}: {
  shipment: Shipment;
  onUpdated: () => Promise<void> | void;
}) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState(
    OVERRIDE_STATUSES.includes(shipment.status) ? shipment.status : "in_transit",
  );
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (CLOSED_STATUSES.includes(shipment.status)) return null;

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api<Shipment>(`/ops/shipments/${shipment.id}/tracking`, {
        method: "POST",
        body: { status, note: note.trim() || null },
      });
      setOpen(false);
      setNote("");
      await onUpdated();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!open) {
    return (
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => setOpen(true)}>
        Update tracking
      </button>
    );
  }

  return (
    <form onSubmit={submit} style={{ marginTop: 8 }}>
      <div className="row" style={{ gap: 8, flexWrap: "wrap" }}>
        <select value={status} onChange={(event) => setStatus(event.target.value)} aria-label="Tracking status">
          {OVERRIDE_STATUSES.map((value) => (
            <option key={value} value={value}>
              {value.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <input
          value={note}
          onChange={(event) => setNote(event.target.value)}
          placeholder="Note shown to the customer (optional)"
          maxLength={500}
          style={{ flex: "1 1 220px" }}
        />
        <button type="submit" className="btn btn-primary btn-sm" disabled={busy}>
          {busy ? "Saving…" : "Save update"}
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => setOpen(false)} disabled={busy}>
          Cancel
        </button>
      </div>
      {error ? (
        <p className="small" style={{ color: "var(--danger)", marginTop: 6 }}>
          {error}
        </p>
      ) : (
        <p className="tiny faint" style={{ marginTop: 6 }}>
          Manual updates pause simulated carrier events for this batch.
        </p>
      )}
    </form>
  );
}
