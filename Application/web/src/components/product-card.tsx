import Link from "next/link";

import { money, titleCase } from "@/lib/format";
import type { ProductSummary } from "@/lib/types";

import { Badge, Thumb } from "./ui";

export function ProductCard({ product }: { product: ProductSummary }) {
  const price =
    product.price_from === product.price_to
      ? money(product.price_from)
      : `${money(product.price_from)} – ${money(product.price_to)}`;

  return (
    <Link href={`/product/${product.slug}`} className="product-card">
      <Thumb name={product.name} />
      <div className="product-body">
        <div className="row-wrap" style={{ gap: 6 }}>
          {product.department_name ?? product.department_slug ? (
            <span className="tiny faint">
              {product.department_name ?? titleCase(product.department_slug)}
            </span>
          ) : null}
          {product.in_stock ? null : <Badge tone="red">Sold out</Badge>}
        </div>
        <div className="product-name">{product.name}</div>
        <div className="product-meta">
          {product.supplier}
          {product.brand ? ` · ${product.brand}` : ""}
        </div>
        <div className="product-price">
          <span className="price">{price}</span>
          <span className="small faint">{product.variant_count > 1 ? `${product.variant_count} options` : ""}</span>
        </div>
      </div>
    </Link>
  );
}
