import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <div className="brand" style={{ marginBottom: 12 }}>
            <span className="brand-mark">u</span>
            <span>Usiri</span>
          </div>
          <p style={{ maxWidth: "34ch" }}>
            A managed marketplace for Tanzanian homes. Verified suppliers, licensed carriers and
            payments through authorised providers.
          </p>
          <p className="small" style={{ marginTop: 14 }}>
            Demo build · no real payments are taken.
          </p>
        </div>
        <div>
          <h4>Shop</h4>
          <Link href="/shop">All products</Link>
          <Link href="/shop?department=homeware-storage">Homeware &amp; storage</Link>
          <Link href="/shop?department=small-appliances">Small appliances</Link>
          <Link href="/shop?department=bundles">Bundles</Link>
        </div>
        <div>
          <h4>Your account</h4>
          <Link href="/orders">Orders</Link>
          <Link href="/cart">Cart</Link>
          <Link href="/support">Support</Link>
          <Link href="/register">Create account</Link>
        </div>
        <div>
          <h4>Partners</h4>
          <Link href="/login">Supplier portal</Link>
          <Link href="/ops">Operations console</Link>
          <p style={{ marginTop: 12 }}>msaada@usiri.co.tz</p>
          <p>Dar es Salaam, Tanzania</p>
        </div>
      </div>
    </footer>
  );
}
