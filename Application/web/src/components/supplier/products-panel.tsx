"use client";

import { useState } from "react";

import { Alert, StatusBadge } from "@/components/ui";
import { api } from "@/lib/api";
import { money } from "@/lib/format";
import type { Department, SupplierProduct, SupplierVariantRow } from "@/lib/types";

export function SupplierProductsPanel({
  products,
  departments,
  onChanged,
}: {
  products: SupplierProduct[];
  departments: Department[];
  onChanged: () => Promise<void>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [notice, setNotice] = useState("");

  return (
    <div className="stack">
      <div className="spread">
        <p className="muted small" style={{ maxWidth: "56ch" }}>
          Prices are in TZS. Stock you set is what customers can buy; reserved units are already
          committed to paid orders.
        </p>
        <button type="button" className="btn btn-primary btn-sm" onClick={() => setShowForm((value) => !value)}>
          {showForm ? "Close form" : "Add a product"}
        </button>
      </div>

      {notice ? <Alert kind="success">{notice}</Alert> : null}

      {showForm ? (
        <NewProductForm
          departments={departments}
          onCreated={async (name) => {
            setShowForm(false);
            setNotice(`${name} created.`);
            await onChanged();
          }}
        />
      ) : null}

      {products.length === 0 ? (
        <p className="muted">You have no products yet. Add the first one above.</p>
      ) : (
        <div className="stack-sm">
          {products.map((product) => (
            <article key={product.id} className="card">
              <div className="card-pad" style={{ paddingBottom: 12 }}>
                <div className="spread" style={{ alignItems: "flex-start" }}>
                  <div>
                    <div className="row" style={{ gap: 10 }}>
                      <strong>{product.name}</strong>
                      <StatusBadge status={product.status} />
                    </div>
                    <div className="small faint" style={{ marginTop: 4 }}>
                      {product.brand ? `${product.brand} · ` : ""}
                      {product.variants.length} variant{product.variants.length === 1 ? "" : "s"} ·{" "}
                      {product.slug}
                    </div>
                  </div>
                  <div className="small muted right">
                    {money(product.price_from)}
                    {product.price_to !== product.price_from ? ` – ${money(product.price_to)}` : ""}
                  </div>
                </div>
              </div>

              <div className="table-wrap" style={{ border: "none", borderRadius: 0 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Variant</th>
                      <th>Price (TZS)</th>
                      <th>On hand</th>
                      <th>Reserved</th>
                      <th>Available</th>
                      <th>Active</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {product.variants.map((variant) => (
                      <VariantEditor key={variant.id} variant={variant} onSaved={onChanged} />
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function VariantEditor({
  variant,
  onSaved,
}: {
  variant: SupplierVariantRow;
  onSaved: () => Promise<void>;
}) {
  const [price, setPrice] = useState(String(variant.price));
  const [onHand, setOnHand] = useState(String(variant.on_hand));
  const [active, setActive] = useState(variant.active);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const dirty =
    Number(price) !== variant.price || Number(onHand) !== variant.on_hand || active !== variant.active;

  async function save() {
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await api(`/supplier/variants/${variant.id}`, {
        method: "PATCH",
        body: {
          price: Number(price),
          on_hand: Number(onHand),
          active,
        },
      });
      setSaved(true);
      await onSaved();
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <tr>
        <td>
          <div style={{ fontWeight: 600 }}>{variant.name}</div>
          <div className="small faint">{variant.sku}</div>
          {error ? (
            <div className="small" style={{ color: "var(--danger)", marginTop: 4 }}>
              {error}
            </div>
          ) : null}
        </td>
        <td>
          <input
            type="number"
            min={1000}
            value={price}
            onChange={(event) => setPrice(event.target.value)}
            style={{ width: 110 }}
            aria-label={`Price for ${variant.name}`}
          />
        </td>
        <td>
          <input
            type="number"
            min={0}
            value={onHand}
            onChange={(event) => setOnHand(event.target.value)}
            style={{ width: 90 }}
            aria-label={`On hand for ${variant.name}`}
          />
        </td>
        <td>{variant.reserved}</td>
        <td>{variant.available}</td>
        <td>
          <input
            type="checkbox"
            checked={active}
            onChange={(event) => setActive(event.target.checked)}
            style={{ width: 16, height: 16, accentColor: "var(--brand)" }}
            aria-label={`Active for ${variant.name}`}
          />
        </td>
        <td className="right">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={save}
            disabled={busy || !dirty}
          >
            {busy ? "Saving…" : saved && !dirty ? "Saved" : "Save"}
          </button>
        </td>
      </tr>
    </>
  );
}

function NewProductForm({
  departments,
  onCreated,
}: {
  departments: Department[];
  onCreated: (name: string) => Promise<void>;
}) {
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [description, setDescription] = useState("");
  const [departmentId, setDepartmentId] = useState(departments[0]?.id ?? "");
  const [categoryId, setCategoryId] = useState("");
  const [variantName, setVariantName] = useState("Default");
  const [price, setPrice] = useState("25000");
  const [stock, setStock] = useState("10");
  const [weight, setWeight] = useState("500");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const categories = departments.find((entry) => entry.id === departmentId)?.categories ?? [];

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api<SupplierProduct>("/supplier/products", {
        method: "POST",
        body: {
          name: name.trim(),
          brand: brand.trim() || null,
          description: description.trim(),
          department_id: departmentId,
          category_id: categoryId || null,
          variants: [
            {
              name: variantName.trim() || "Default",
              price: Number(price),
              on_hand: Number(stock),
              weight_g: Number(weight),
            },
          ],
        },
      });
      await onCreated(name.trim());
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card card-pad" onSubmit={submit}>
      <h2 style={{ fontSize: "1.05rem", marginBottom: 14 }}>New product</h2>
      {error ? <div style={{ marginBottom: 12 }}><Alert kind="error">{error}</Alert></div> : null}
      <div className="form-grid">
        <label className="field">
          <span>Product name</span>
          <input value={name} onChange={(event) => setName(event.target.value)} minLength={3} required />
        </label>
        <label className="field">
          <span>Brand (optional)</span>
          <input value={brand} onChange={(event) => setBrand(event.target.value)} />
        </label>
        <label className="field">
          <span>Department</span>
          <select
            value={departmentId}
            onChange={(event) => {
              setDepartmentId(event.target.value);
              setCategoryId("");
            }}
            required
          >
            {departments.map((department) => (
              <option key={department.id} value={department.id}>
                {department.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Category (optional)</span>
          <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
            <option value="">No category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field span-2">
          <span>Description</span>
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} />
        </label>
        <label className="field">
          <span>Variant name</span>
          <input value={variantName} onChange={(event) => setVariantName(event.target.value)} />
        </label>
        <label className="field">
          <span>Price (TZS)</span>
          <input type="number" min={1000} value={price} onChange={(event) => setPrice(event.target.value)} required />
        </label>
        <label className="field">
          <span>Stock on hand</span>
          <input type="number" min={0} value={stock} onChange={(event) => setStock(event.target.value)} />
        </label>
        <label className="field">
          <span>Weight (grams)</span>
          <input type="number" min={50} value={weight} onChange={(event) => setWeight(event.target.value)} />
        </label>
      </div>
      <button type="submit" className="btn btn-primary" style={{ marginTop: 16 }} disabled={busy}>
        {busy ? "Creating…" : "Create product"}
      </button>
    </form>
  );
}
