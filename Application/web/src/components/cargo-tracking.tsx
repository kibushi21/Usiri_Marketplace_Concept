"use client";

import { useState } from "react";

import { StatusBadge } from "@/components/ui";
import { date, titleCase } from "@/lib/format";
import type { Order } from "@/lib/types";

const ACTOR_LABELS: Record<string, string> = {
  carrier: "Carrier update",
  operations: "Operations team",
  supplier: "Supplier",
  system: "Usiri system",
};

export function CargoTracking({ order, onRefresh }: { order: Order; onRefresh: () => Promise<void> | void }) {
  const [refreshing, setRefreshing] = useState(false);
  const batches = order.supplier_orders.flatMap((supplierOrder) =>
    supplierOrder.shipments.map((shipment) => ({
      shipment,
      supplierName: supplierOrder.supplier?.name ?? supplierOrder.code,
      supplierOrderCode: supplierOrder.code,
    })),
  );

  if (batches.length === 0) return null;

  async function refresh() {
    setRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  }

  return (
    <section className="stack" style={{ marginBottom: 28 }}>
      <div className="spread" style={{ alignItems: "flex-end" }}>
        <div>
          <h2 style={{ fontSize: "1.05rem" }}>Cargo tracking</h2>
          <p className="small faint" style={{ marginTop: 4 }}>
            Each supplier ships its own batch. Follow every batch below from dispatch to delivery.
          </p>
        </div>
        <button type="button" className="btn btn-secondary btn-sm" onClick={refresh} disabled={refreshing}>
          {refreshing ? "Refreshing…" : "Refresh tracking"}
        </button>
      </div>
      <div className="stack-sm">
        {batches.map((batch, index) => (
          <BatchCard key={batch.shipment.id} {...batch} index={index} />
        ))}
      </div>
    </section>
  );
}

function BatchCard({
  shipment,
  supplierName,
  supplierOrderCode,
  index,
}: {
  shipment: Order["supplier_orders"][number]["shipments"][number];
  supplierName: string;
  supplierOrderCode: string;
  index: number;
}) {
  const events = [...shipment.events].sort(
    (a, b) => new Date(a.occurred_at).getTime() - new Date(b.occurred_at).getTime(),
  );
  const latest = events[events.length - 1];

  return (
    <section className="card">
      <div className="card-pad" style={{ paddingBottom: 12 }}>
        <div className="spread" style={{ alignItems: "flex-start" }}>
          <div>
            <div className="tiny faint">Cargo batch {index + 1}</div>
            <div className="row" style={{ gap: 8, marginTop: 4 }}>
              <strong>{supplierName}</strong>
              <StatusBadge status={shipment.status} />
            </div>
            <div className="small muted" style={{ marginTop: 4 }}>
              {shipment.carrier} ·{" "}
              <span style={{ fontFamily: "ui-monospace, monospace" }}>
                {shipment.tracking_number ?? "no reference yet"}
              </span>
            </div>
          </div>
          <div className="right small faint">
            <div>{supplierOrderCode}</div>
            <div>
              {latest
                ? `Updated ${date(latest.occurred_at)}`
                : shipment.booked_at
                  ? `Booked ${date(shipment.booked_at)}`
                  : "Not yet dispatched"}
            </div>
          </div>
        </div>
      </div>
      <div className="card-pad" style={{ borderTop: "1px solid var(--line)" }}>
        {events.length === 0 ? (
          <p className="muted small">No tracking updates yet. The carrier will post each milestone here.</p>
        ) : (
          <div className="timeline">
            {events.map((event, eventIndex) => (
              <div key={event.id} className="timeline-item">
                <span className={`timeline-dot ${eventIndex === events.length - 1 ? "current" : "done"}`} />
                <div>
                  <div className="spread">
                    <span style={{ fontSize: ".9rem", fontWeight: 600 }}>{titleCase(event.status)}</span>
                    <span className="tiny faint">{date(event.occurred_at)}</span>
                  </div>
                  <div className="small faint">
                    {event.note ? `${event.note} · ` : ""}
                    {ACTOR_LABELS[event.actor] ?? event.actor}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
