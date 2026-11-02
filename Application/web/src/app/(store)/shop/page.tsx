"use client";

import { useEffect, useState } from "react";

import { ProductCard } from "@/components/product-card";
import { PhotoSearch } from "@/components/photo-search";
import { Alert, Empty, Loading } from "@/components/ui";
import { api } from "@/lib/api";
import type { Department, PhotoSearchResult, ProductPage, ProductSummary } from "@/lib/types";

const PAGE_SIZE = 24;

const SORTS = [
  { id: "featured", label: "Newest" },
  { id: "price_asc", label: "Price: low to high" },
  { id: "price_desc", label: "Price: high to low" },
  { id: "name", label: "Name A–Z" },
];

function PhotoIcon() {
  return (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="3" y="4" width="18" height="16" rx="3" />
      <circle cx="8.5" cy="9.5" r="1.5" />
      <path d="M21 15l-5-5L5 21" />
    </svg>
  );
}

export default function ShopPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [department, setDepartment] = useState("");
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("featured");
  const [items, setItems] = useState<ProductSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [photo, setPhoto] = useState<{ result: PhotoSearchResult; filename: string } | null>(null);
  const [photoOpen, setPhotoOpen] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialDepartment = params.get("department") ?? "";
    const initialQuery = params.get("q") ?? "";
    setDepartment(initialDepartment);
    setInput(initialQuery);
    setQuery(initialQuery);
    api<Department[]>("/catalogue/departments", { auth: false })
      .then(setDepartments)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: "0", sort });
    if (department) params.set("department", department);
    if (query) params.set("q", query);
    api<ProductPage>(`/catalogue/products?${params.toString()}`, { auth: false })
      .then((page) => {
        if (!active) return;
        setItems(page.items);
        setTotal(page.total);
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
  }, [department, query, sort]);

  async function loadMore() {
    setLoadingMore(true);
    try {
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        offset: String(items.length),
        sort,
      });
      if (department) params.set("department", department);
      if (query) params.set("q", query);
      const page = await api<ProductPage>(`/catalogue/products?${params.toString()}`, {
        auth: false,
      });
      setItems((current) => [...current, ...page.items]);
      setTotal(page.total);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setLoadingMore(false);
    }
  }

  const activeDepartment = departments.find((entry) => entry.slug === department);

  return (
    <div className="container">
      <div className="portal-head">
        <div>
          <div className="tiny faint" style={{ marginBottom: 8 }}>
            Catalogue
          </div>
          <h1>{activeDepartment ? activeDepartment.name : "Everything on Usiri"}</h1>
          <p className="muted" style={{ marginTop: 8 }}>
            {loading
              ? "Loading products…"
              : photo
                ? `${photo.result.total} ${photo.result.total === 1 ? "match" : "matches"} from your photo`
                : `${total} ${total === 1 ? "product" : "products"} from verified suppliers`}
          </p>
        </div>
        <form
          className="search"
          onSubmit={(event) => {
            event.preventDefault();
            setPhoto(null);
            setPhotoOpen(false);
            setQuery(input.trim());
          }}
        >
          <div className="search-field">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Search products, brands…"
              aria-label="Search products"
            />
            <button
              type="button"
              className={`search-photo${photoOpen ? " active" : ""}`}
              onClick={() => setPhotoOpen((current) => !current)}
              aria-label="Search by photo"
              aria-expanded={photoOpen}
              title="Search by photo"
            >
              <PhotoIcon />
            </button>
          </div>
          <button className="btn btn-primary btn-sm" type="submit">
            Search
          </button>
        </form>
      </div>

      <PhotoSearch
        open={photoOpen}
        onClose={() => setPhotoOpen(false)}
        onResults={(result, filename) => setPhoto({ result, filename })}
      />

      {photo ? (
        <section className="card card-pad" style={{ marginBottom: 18 }}>
          <div className="spread" style={{ alignItems: "flex-start" }}>
            <div>
              <div className="row" style={{ gap: 8 }}>
                <strong>Photo matches</strong>
                <span className="small faint">{photo.filename}</span>
              </div>
              {photo.result.tags.length > 0 ? (
                <div className="row" style={{ gap: 6, flexWrap: "wrap", marginTop: 10 }}>
                  {photo.result.tags.map((tag) => (
                    <span key={tag} className="badge badge-neutral">
                      {tag}
                    </span>
                  ))}
                </div>
              ) : null}
              <p className="small faint" style={{ marginTop: 10 }}>
                {photo.result.note}
              </p>
              {photo.result.total === 0 ? (
                <p className="small muted" style={{ marginTop: 6 }}>
                  No catalogue products matched. Try another photo or add a hint like “kettle”.
                </p>
              ) : null}
            </div>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => setPhoto(null)}
            >
              Clear photo search
            </button>
          </div>
        </section>
      ) : null}

      {photo ? null : (
        <div className="filter-bar">
        <div className="chip-row">
          <button
            type="button"
            className={`chip${department === "" ? " active" : ""}`}
            onClick={() => setDepartment("")}
          >
            All departments
          </button>
          {departments.map((entry) => (
            <button
              key={entry.id}
              type="button"
              className={`chip${department === entry.slug ? " active" : ""}`}
              onClick={() => setDepartment(entry.slug)}
            >
              {entry.name}
            </button>
          ))}
        </div>
        <div className="row" style={{ gap: 10 }}>
          {query ? (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setQuery("");
                setInput("");
              }}
            >
              Clear “{query}”
            </button>
          ) : null}
          <select
            value={sort}
            onChange={(event) => setSort(event.target.value)}
            aria-label="Sort products"
            style={{ width: "auto" }}
          >
            {SORTS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        </div>
      )}

      {error ? <Alert kind="error">{error}</Alert> : null}

      {loading && !photo ? (
        <Loading label="Fetching the shelves…" />
      ) : (photo ? photo.result.items : items).length === 0 ? (
        <Empty
          title={photo ? "No products matched that photo" : "Nothing matches that yet"}
          action={
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => {
                if (photo) {
                  setPhoto(null);
                  return;
                }
                setDepartment("");
                setQuery("");
                setInput("");
              }}
            >
              {photo ? "Clear photo search" : "Reset filters"}
            </button>
          }
        >
          {photo
            ? "Try a different photo, or add a hint like “kettle” so the demo can match it."
            : query
              ? `We could not find products matching “${query}”. Try a different word or browse a department.`
              : "This department has no products yet. Check back soon."}
        </Empty>
      ) : (
        <>
          <div className="product-grid">
            {(photo ? photo.result.items : items).map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
          {!photo && items.length < total ? (
            <div className="pager">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={loadMore}
                disabled={loadingMore}
              >
                {loadingMore ? "Loading…" : `Load ${Math.min(PAGE_SIZE, total - items.length)} more`}
              </button>
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}
