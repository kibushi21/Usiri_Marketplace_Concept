"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { homeForRole, useAuth } from "@/lib/auth";
import { CART_EVENT } from "@/lib/session";
import { initials } from "@/lib/format";
import type { Cart } from "@/lib/types";

const ROLE_LABEL: Record<string, string> = {
  customer: "Customer",
  supplier: "Supplier",
  ops_admin: "Operations",
  ops_finance: "Finance",
  ops_support: "Support",
  superadmin: "Administrator",
};

export function SiteHeader() {
  const { user, token, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [cartCount, setCartCount] = useState(0);

  const isCustomer = user?.role === "customer";
  const isStaff = user ? ["ops_admin", "ops_finance", "ops_support", "superadmin"].includes(user.role) : false;

  useEffect(() => {
    if (!token || !isCustomer) {
      setCartCount(0);
      return;
    }
    let active = true;
    const load = () => {
      api<Cart>("/cart", { token })
        .then((cart) => {
          if (active) setCartCount(cart.item_count);
        })
        .catch(() => {
          if (active) setCartCount(0);
        });
    };
    load();
    window.addEventListener(CART_EVENT, load);
    return () => {
      active = false;
      window.removeEventListener(CART_EVENT, load);
    };
  }, [token, isCustomer, pathname]);

  const link = (href: string, label: string, className?: string) => {
    const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
    return (
      <Link key={href} href={href} aria-current={active ? "page" : undefined} className={className}>
        {label}
      </Link>
    );
  };

  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link href="/" className="brand" aria-label="Usiri home">
          <span className="brand-mark">u</span>
          <span>Usiri</span>
        </Link>

        <nav className="nav" aria-label="Primary">
          {link("/shop", "Shop")}
          {isCustomer ? link("/orders", "Orders") : null}
          {isCustomer ? link("/support", "Support") : null}
          {user?.role === "supplier" ? link("/supplier", "Supplier portal") : null}
          {isStaff ? link("/ops", "Operations") : null}
          {!user ? link("/login", "Sell on Usiri", "hide-sm") : null}
        </nav>

        <div className="header-actions">
          {isCustomer ? (
            <Link href="/cart" className="cart-link" aria-label="Cart">
              Cart
              <span className="cart-count">{cartCount}</span>
            </Link>
          ) : null}

          {user ? (
            <details className="account">
              <summary>
                <span className="avatar">{initials(user.full_name)}</span>
                <span>{user.full_name.split(" ")[0]}</span>
              </summary>
              <div className="account-menu">
                <div className="menu-label">
                  {ROLE_LABEL[user.role] ?? user.role} · {user.email}
                </div>
                {isCustomer ? <Link href="/orders">My orders</Link> : null}
                {isCustomer ? <Link href="/support">Support</Link> : null}
                {user.role === "supplier" ? <Link href="/supplier">Supplier portal</Link> : null}
                {isStaff ? <Link href="/ops">Operations console</Link> : null}
                <Link href={homeForRole(user.role)}>Account home</Link>
                <button
                  type="button"
                  onClick={() => {
                    logout();
                    router.push("/");
                  }}
                >
                  Sign out
                </button>
              </div>
            </details>
          ) : (
            <>
              <Link href="/login" className="btn btn-ghost btn-sm">
                Log in
              </Link>
              <Link href="/register" className="btn btn-primary btn-sm">
                Create account
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
