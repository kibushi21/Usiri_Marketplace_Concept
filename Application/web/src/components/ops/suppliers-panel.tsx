"use client";

import { useCallback, useEffect, useState } from "react";

import { Alert, Loading, Stat, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { money, percent, titleCase } from "@/lib/format";
import type { SupplierDirectoryEntry, SupplierProfile } from "@/lib/types";

export function OpsSuppliersPanel({ canManage }: { canManage: boolean }) {
  const [suppliers, setSuppliers] = useState<SupplierDirectoryEntry[]>([]);
  const [selected, setSelected] = useState<SupplierProfile | null>(null);
  const [commission, setCommission] = useState("");
  const [busy, setBusy] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadList = useCallback(async () => {
    const data = await api<{ items: SupplierDirectoryEntry[] }>("/ops/suppliers");
    setSuppliers(data.items);
  }, []);

  const open = useCallback(async (supplierId: string) => {
    setBusy("open");
    setError("");
    setNotice("");
    try {
      const profile = await api<SupplierProfile>(`/ops/suppliers/${supplierId}`);
      setSelected(profile);
      setCommission(profile.commission_bp === null ? "" : String(profile.commission_bp));
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }, []);

  useEffect(() => {
    let active = true;
    loadList()
      .catch((cause: Error) => {
        if (active) setError(cause.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadList]);

  async function patch(body: Record<string, unknown>, message: string) {
    if (!selected) return;
    setBusy("patch");
    setError("");
    setNotice("");
    try {
      await api(`/ops/suppliers/${selected.id}`, { method: "PATCH", body });
      await loadList();
      await open(selected.id);
      setNotice(message);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy("");
    }
  }

  if (loading) return <Loading label="Loading suppliers…" />;

  if (selected) {
    return (
      <div className="stack">
        <div className="spread">
          <button type="button" className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>
            ← All suppliers
          </button>
          <StatusBadge status={selected.status} />
        </div>

        {error ? <Alert kind="error">{error}</Alert> : null}
        {notice ? <Alert kind="success">{notice}</Alert> : null}

        <div className="card card-pad">
          <div className="spread" style={{ alignItems: "flex-start" }}>
            <div>
              <h2 style={{ fontSize: "1.35rem" }}>{selected.trading_name}</h2>
              <p className="muted small" style={{ marginTop: 4 }}>
                {selected.legal_name} · {selected.code} · {selected.city}, {selected.region}
              </p>
              <p className="small faint" style={{ marginTop: 4 }}>
                TIN {selected.tin} · BRELA {selected.brela_number} · rated {selected.rating.toFixed(1)}
              </p>
            </div>
            <div className="right small">
              <div>{selected.contact_name ?? "—"}</div>
              <div className="muted">{selected.contact_email ?? "—"}</div>
              <div className="muted">{selected.contact_phone ?? "—"}</div>
            </div>
          </div>

          <div className="stat-grid" style={{ marginTop: 20 }}>
            <Stat label="Eligible" value={money(selected.balance.eligible)} />
            <Stat label="In payout" value={money(selected.balance.in_payout)} />
            <Stat label="Settled" value={money(selected.balance.settled)} />
            <Stat label="Products" value={selected.products.length} />
          </div>

          {canManage ? (
            <>
              <hr className="divider" />
              <div className="inline-form">
                <label className="field" style={{ maxWidth: 220 }}>
                  <span>Commission (basis points)</span>
                  <input
                    type="number"
                    min={0}
                    max={3000}
                    value={commission}
                    onChange={(event) => setCommission(event.target.value)}
                    placeholder="800 = 8%"
                  />
                </label>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={busy === "patch" || commission === "" || Number(commission) === selected.commission_bp}
                  onClick={() => patch({ commission_bp: Number(commission) }, "Commission updated.")}
                >
                  Save commission
                </button>
                <span className="small faint">
                  Effective {commission ? percent(Number(commission)) : "platform default"}
                </span>
              </div>
              <div className="btn-row" style={{ marginTop: 14 }}>
                {selected.status !== "verified" ? (
                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    disabled={busy === "patch"}
                    onClick={() => patch({ status: "verified" }, "Supplier verified and documents approved.")}
                  >
                    Verify supplier
                  </button>
                ) : null}
                {selected.status !== "suspended" ? (
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    disabled={busy === "patch"}
                    onClick={() => patch({ status: "suspended" }, "Supplier suspended. Products are hidden.")}
                  >
                    Suspend
                  </button>
                ) : null}
              </div>
            </>
          ) : (
            <p className="small faint" style={{ marginTop: 14 }}>
              Only operations administrators can change commission or supplier status.
            </p>
          )}
        </div>

        <div className="split">
          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Documents</h3>
            <div className="table-wrap" style={{ border: "none" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  {selected.documents.map((document) => (
                    <tr key={document.id}>
                      <td>{titleCase(document.type)}</td>
                      <td>
                        <StatusBadge status={document.status} />
                      </td>
                      <td className="small faint">{document.file_ref ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card card-pad">
            <h3 style={{ fontSize: "1rem", marginBottom: 10 }}>Payout account</h3>
            <div className="kv">
              <div>
                <span>Method</span>
                <strong>{titleCase(selected.payout.method)}</strong>
              </div>
              <div>
                <span>Provider</span>
                <strong>{selected.payout.provider}</strong>
              </div>
              <div>
                <span>Account name</span>
                <strong>{selected.payout.account_name}</strong>
              </div>
              <div>
                <span>Account number</span>
                <strong>{selected.payout.account_number}</strong>
              </div>
            </div>
          </section>
        </div>

        <section className="card">
          <div className="card-pad" style={{ paddingBottom: 12 }}>
            <h3 style={{ fontSize: "1rem" }}>Products</h3>
          </div>
          <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Status</th>
                  <th className="right">Variants</th>
                  <th className="right">Stock</th>
                </tr>
              </thead>
              <tbody>
                {selected.products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.name}</td>
                    <td>
                      <StatusBadge status={product.status} />
                    </td>
                    <td className="right">{product.variants}</td>
                    <td className="right">{product.stock}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="stack">
      {error ? <Alert kind="error">{error}</Alert> : null}
      {busy === "open" ? <Loading label="Opening supplier…" /> : null}
      <p className="small muted">
        {suppliers.length} suppliers. Verify onboarding documents before a supplier can sell.
      </p>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Supplier</th>
              <th>Code</th>
              <th>Region</th>
              <th>Status</th>
              <th className="right">Products</th>
              <th className="right">Rating</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {suppliers.map((supplier) => (
              <tr key={supplier.id}>
                <td>
                  <div style={{ fontWeight: 600 }}>{supplier.name}</div>
                  <div className="small faint">{supplier.legal_name}</div>
                </td>
                <td className="small">{supplier.code}</td>
                <td>{supplier.region}</td>
                <td>
                  <StatusBadge status={supplier.status} />
                </td>
                <td className="right">{supplier.products}</td>
                <td className="right">{supplier.rating.toFixed(1)}</td>
                <td className="right">
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => open(supplier.id)}>
                    Open
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
