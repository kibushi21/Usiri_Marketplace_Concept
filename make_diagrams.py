"""Generate the concept-pack diagrams as standalone SVG files."""

from pathlib import Path

OUT = Path(__file__).parent / "diagrams"
OUT.mkdir(exist_ok=True)

NAVY = "#1F3A5F"
TEAL = "#2A7F7F"
AMBER = "#C8892A"
GREY = "#5A6572"
LIGHT = "#F4F7FA"
WHITE = "#FFFFFF"

DEFS = f"""
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{NAVY}"/>
  </marker>
  <marker id="arrowTeal" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{TEAL}"/>
  </marker>
  <marker id="arrowAmber" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{AMBER}"/>
  </marker>
  <filter id="shadow" x="-4%" y="-4%" width="108%" height="112%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.08"/>
  </filter>
</defs>
"""

STYLE = f"""
<style>
  .title {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 25px; font-weight: bold; fill: {NAVY}; }}
  .subtitle {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 13px; fill: {GREY}; }}
  .box {{ fill: {WHITE}; stroke: {NAVY}; stroke-width: 1.4; }}
  .brand {{ fill: {NAVY}; stroke: {NAVY}; }}
  .ops {{ fill: #E9F2F1; stroke: {TEAL}; }}
  .ext {{ fill: #FCF3E4; stroke: {AMBER}; }}
  .light {{ fill: {LIGHT}; stroke: #CBD5E1; }}
  .h {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: {NAVY}; }}
  .hw {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 15px; font-weight: bold; fill: {WHITE}; }}
  .t {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 12.5px; fill: #333333; }}
  .tw {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 12.5px; fill: {WHITE}; }}
  .s {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11px; fill: {GREY}; }}
  .tag {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11px; font-weight: bold; fill: {TEAL}; letter-spacing: 0.6px; }}
  .arrow {{ stroke: {NAVY}; stroke-width: 1.6; fill: none; marker-end: url(#arrow); }}
  .conn {{ stroke: {NAVY}; stroke-width: 1.6; fill: none; }}
  .arrow-teal {{ stroke: {TEAL}; stroke-width: 1.6; fill: none; marker-end: url(#arrowTeal); }}
  .arrow-amber {{ stroke: {AMBER}; stroke-width: 1.6; fill: none; marker-end: url(#arrowAmber); }}
  .dash {{ stroke-dasharray: 7 5; }}
  .dot {{ stroke-dasharray: 2 4; }}
  .lane {{ fill: #FFFFFF; stroke: #D8E0E8; stroke-width: 1; }}
  .lane-alt {{ fill: #F8FAFC; stroke: #D8E0E8; stroke-width: 1; }}
  .cell-blue {{ fill: #E4EDF7; stroke: #B8CCE2; }}
  .cell-teal {{ fill: #E3F0EE; stroke: #B9D8D4; }}
  .cell-amber {{ fill: #FBEFD8; stroke: #E7CC9B; }}
  .cell-grey {{ fill: #EEF2F6; stroke: #D3DCE5; }}
  .note {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 10.5px; fill: {GREY}; }}
</style>
"""


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def text_block(x, y, lines, cls="t", anchor="middle", lh=16):
    out = []
    for i, line in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i * lh}" class="{cls}" text-anchor="{anchor}">{esc(line)}</text>')
    return "\n".join(out)


def box(x, y, w, h, lines, cls="box", hcls="h", tcls="t", rx=10, shadow=True):
    filt = ' filter="url(#shadow)"' if shadow else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"{filt}/>']
    # first line is heading
    out.append(f'<text x="{x + w/2}" y="{y + 24}" class="{hcls}" text-anchor="middle">{esc(lines[0])}</text>')
    if len(lines) > 1:
        out.append(text_block(x + w / 2, y + 44, lines[1:], tcls, lh=15))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, cls="arrow", label=None, lx=None, ly=None, anchor="middle"):
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>']
    if label:
        out.append(f'<text x="{lx if lx is not None else (x1+x2)/2}" y="{ly if ly is not None else (y1+y2)/2 - 6}" class="s" text-anchor="{anchor}">{esc(label)}</text>')
    return "\n".join(out)


def path(d, cls="arrow", label=None, lx=0, ly=0, anchor="middle"):
    out = [f'<path d="{d}" class="{cls}"/>']
    if label:
        out.append(f'<text x="{lx}" y="{ly}" class="s" text-anchor="{anchor}">{esc(label)}</text>')
    return "\n".join(out)


def svg(width, height, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{DEFS}{STYLE}<rect width="100%" height="100%" fill="#FFFFFF"/>\n{body}\n</svg>'


# ---------------------------------------------------------------------------
# 1. Business model ecosystem
# ---------------------------------------------------------------------------
b = []
b.append('<text x="45" y="48" class="title">Proposed business model: a managed, asset-light marketplace</text>')
b.append('<text x="45" y="72" class="subtitle">Concept only. No franchise, brand licence, logistics or payment agreement has been concluded.</text>')

b.append(box(500, 105, 400, 82, ["USIRI GROUP (potential)", "Brand owner and logistics partner"], "brand", "hw", "tw"))
b.append(box(500, 330, 400, 120, ["MARKETPLACE OPERATOR", "Founders' Tanzanian company", "Platform · suppliers · orders · support"], "ops", "h", "t"))
b.append(box(80, 330, 290, 120, ["VERIFIED SUPPLIERS", "Wholesalers, distributors", "and manufacturers"], "box", "h", "t"))
b.append(box(1030, 330, 290, 120, ["CUSTOMERS", "Dar es Salaam first", "Upcountry collection points"], "box", "h", "t"))
b.append(box(550, 580, 300, 90, ["CONTRACTED CARRIER(S)", "Usiri or a qualified alternative"], "ext", "h", "t"))

# brand relationship
b.append(arrow(690, 187, 690, 330, "arrow-amber dash", "brand licence, standards,", 705, 245, "start"))
b.append('<text x="705" y="261" class="s" text-anchor="start">logistics capacity (proposed)</text>')

# supplier <-> operator
b.append(arrow(370, 375, 500, 375, "arrow", "products, stock", 435, 365, "middle"))
b.append(arrow(500, 415, 370, 415, "arrow", "orders, payouts", 435, 433, "middle"))

# operator <-> customer
b.append(arrow(900, 375, 1030, 375, "arrow", "catalogue, checkout", 965, 365, "middle"))
b.append(arrow(1030, 415, 900, 415, "arrow", "orders, payment", 965, 433, "middle"))

# operator <-> carrier
b.append(arrow(680, 450, 680, 580, "arrow", "bookings, manifest", 695, 520, "start"))
b.append(arrow(760, 580, 760, 450, "arrow", "POD, exceptions", 775, 545, "start"))

# carrier -> customer
b.append(path("M 850 625 L 1000 625 L 1000 450", "arrow", "delivery / collection", 1010, 612, "start"))

# regulatory perimeter
b.append(f'<rect x="80" y="700" width="1240" height="48" rx="8" class="light"/>')
b.append('<text x="100" y="721" class="h" font-size="13">Regulatory perimeter</text>')
b.append('<text x="100" y="738" class="s">FCC (consumer contracts) · PDPC (personal data) · Bank of Tanzania (payments) · TCRA (courier licensing) · TRA (tax) · BRELA (company and trademarks)</text>')

# money strip
b.append('<text x="80" y="790" class="tag">MONEY FLOW (SIMPLIFIED)</text>')
money = [
    ("Customer pays", "mobile money, card or bank"),
    ("Licensed PSP collects", "settlement to operator account"),
    ("Operator deducts fees", "commission, coordination fee"),
    ("Supplier is paid", "after delivery confirmation"),
]
mx = 80
for i, (h, s) in enumerate(money):
    b.append(f'<rect x="{mx}" y="802" width="270" height="58" rx="7" class="box"/>')
    b.append(f'<text x="{mx+135}" y="823" class="h" font-size="12.5" text-anchor="middle">{h}</text>')
    b.append(f'<text x="{mx+135}" y="842" class="s" text-anchor="middle">{s}</text>')
    if i < 3:
        b.append(arrow(mx + 272, 831, mx + 310, 831, "arrow-teal"))
    mx += 312

b.append('<text x="45" y="890" class="note">Solid arrows = operational flows. Dashed amber = proposed contractual relationship. Carrier delivery charges are a pass-through, not marketplace revenue.</text>')
svg1 = svg(1400, 910, "\n".join(b))
(OUT / "business_model.svg").write_text(svg1, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2. Workflow swimlane
# ---------------------------------------------------------------------------
w = []
w.append('<text x="45" y="48" class="title">Customer, supplier and logistics workflow</text>')
w.append('<text x="45" y="72" class="subtitle">Eight stages from discovery to settlement and aftercare. Manual coordination is assumed for the pilot.</text>')

stages = [
    ("1. Discover", "Search, compare,\ncheck supplier"),
    ("2. Order & pay", "Cart, delivery\nquote, payment"),
    ("3. Confirm & pack", "Stock check,\npack, label"),
    ("4. Handover", "Drop-off or\npickup, manifest"),
    ("5. Line-haul", "Route, scan,\nin-transit"),
    ("6. Last mile", "Delivery or\ncollection"),
    ("7. Confirm", "POD, status,\nreconcile"),
    ("8. Aftercare", "Payout, returns,\nrefunds, disputes"),
]
lane_x = 40
label_w = 190
col_w = 158
top = 115
header_h = 58
lane_h = 100
lanes = [
    ("CUSTOMER", "cell-blue", [
        "Browses and\ncompares", "Places order;\npays", "", "", "",
        "Receives or\ncollects", "Confirms\ndelivery", "Reviews, returns,\ncomplains"]),
    ("MARKETPLACE", "cell-teal", [
        "Catalogue,\nsearch, ratings", "Checkout,\npayment link", "Routes order;\nmonitors SLA",
        "Books carrier;\nmanifest", "Tracking\nupdates", "Exception\nhandling",
        "Delivery\nconfirmation", "Payout, refund,\ndispute log"]),
    ("SUPPLIER", "cell-amber", [
        "Onboarded;\nlists stock", "", "Confirms stock;\npacks parcel", "Hands parcel\nto carrier",
        "", "", "", "Receives payout;\nhandles return"]),
    ("CARRIER", "cell-grey", [
        "", "", "", "Receives and\nscans parcel", "Line-haul;\nstatus events",
        "Delivers or\nholds at branch", "Returns POD;\ncloses trip", "Reverse\nlogistics"]),
    ("PAYMENT PROVIDER", "cell-grey", [
        "", "Collects funds;\nsends webhook", "", "", "", "", "Settles to\nmarketplace",
        "Processes\nrefunds"]),
]

# header
w.append(f'<rect x="{lane_x}" y="{top}" width="{label_w}" height="{header_h}" class="brand" rx="8"/>')
w.append(f'<text x="{lane_x + label_w/2}" y="{top + 30}" class="hw" text-anchor="middle">ACTOR</text>')
w.append(f'<text x="{lane_x + label_w/2}" y="{top + 47}" class="tw" text-anchor="middle" font-size="10">stage / handoff</text>')
for i, (name, sub) in enumerate(stages):
    x = lane_x + label_w + i * col_w
    w.append(f'<rect x="{x}" y="{top}" width="{col_w}" height="{header_h}" class="light" rx="0"/>')
    w.append(f'<text x="{x + col_w/2}" y="{top + 24}" class="h" text-anchor="middle" font-size="13">{esc(name)}</text>')
    w.append(f'<text x="{x + col_w/2}" y="{top + 42}" class="s" text-anchor="middle">{esc(sub.splitlines()[0])}</text>')
    if len(sub.splitlines()) > 1:
        w.append(f'<text x="{x + col_w/2}" y="{top + 54}" class="s" text-anchor="middle">{esc(sub.splitlines()[1])}</text>')

for r, (lane_name, cls, cells) in enumerate(lanes):
    y = top + header_h + r * lane_h
    w.append(f'<rect x="{lane_x}" y="{y}" width="{label_w}" height="{lane_h}" class="{"lane-alt" if r % 2 else "lane"}"/>')
    w.append(f'<text x="{lane_x + label_w/2}" y="{y + lane_h/2 + 5}" class="h" text-anchor="middle" font-size="13">{lane_name}</text>')
    for c, cell in enumerate(cells):
        x = lane_x + label_w + c * col_w
        w.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{lane_h}" class="{"lane-alt" if r % 2 else "lane"}"/>')
        if cell:
            pad = 9
            w.append(f'<rect x="{x + pad}" y="{y + 22}" width="{col_w - 2*pad}" height="{lane_h - 44}" rx="7" class="{cls}"/>')
            lines = cell.split("\n")
            start_y = y + 47 if len(lines) == 1 else y + 42
            w.append(text_block(x + col_w/2, start_y, lines, "t", lh=15))

# timeline arrow
w.append(f'<line x1="{lane_x + label_w + 5}" y1="{top + header_h + len(lanes)*lane_h + 18}" x2="{lane_x + label_w + len(stages)*col_w - 5}" y2="{top + header_h + len(lanes)*lane_h + 18}" class="arrow"/>')
w.append('<text x="40" y="828" class="note">Multi-supplier orders are split into separate parcels and delivery charges. Each parcel carries its own ID and tracking events.</text>')
w.append('<text x="40" y="846" class="note">Failed delivery: two attempts, then hold at branch for 7 days, then return to supplier. Proof of delivery includes photo and recipient confirmation.</text>')
svg2 = svg(1480, 870, "\n".join(w))
(OUT / "workflow.svg").write_text(svg2, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3. Organisation and responsibility structure
# ---------------------------------------------------------------------------
o = []
o.append('<text x="45" y="48" class="title">Proposed organisation and responsibility structure</text>')
o.append('<text x="45" y="72" class="subtitle">Lean start: founders hold multiple roles. Ownership, equity and titles are not yet agreed.</text>')

o.append(box(540, 100, 300, 72, ["FOUNDERS / BOARD", "Reserved matters: equity, funding, brand deal"], "brand", "hw", "tw"))
o.append(box(540, 225, 300, 72, ["MANAGING DIRECTOR / CEO", "Strategy, partner relations, funding"], "ops", "h", "t"))

o.append(box(100, 370, 250, 96, ["CTO / TECHNOLOGY", "Platform, integrations, security, data"], "box", "h", "t"))
o.append(box(400, 370, 250, 96, ["COO / OPERATIONS", "Suppliers, orders, delivery, support"], "box", "h", "t"))
o.append(box(700, 370, 250, 96, ["FINANCE & COMPLIANCE", "Reconciliation, tax, PDPA, contracts"], "box", "h", "t"))
o.append(box(1000, 370, 250, 96, ["GROWTH & MARKETING", "Acquisition, content, partnerships"], "box", "h", "t"))

o.append(box(100, 550, 250, 100, ["ENGINEERING", "MVP, payments,", "carrier adapter"], "light", "h", "s"))
o.append(box(400, 550, 180, 100, ["SUPPLIER SUCCESS", "KYC, onboarding,", "catalogue"], "light", "h", "s"))
o.append(box(600, 550, 180, 100, ["CUSTOMER SUPPORT", "Swahili/English,", "returns, complaints"], "light", "h", "s"))
o.append(box(800, 550, 180, 100, ["LOGISTICS", "Bookings, manifests,", "exceptions"], "light", "h", "s"))
o.append(box(1020, 550, 270, 100, ["OUTSOURCED ADVISERS", "Lawyer · accountant", "DPO · insurance"], "ext", "h", "s"))

# connectors
o.append(f'<line x1="690" y1="172" x2="690" y2="225" class="arrow"/>')
for x in (225, 525, 825, 1125):
    o.append(f'<path d="M 690 297 L 690 330 L {x} 330 L {x} 370" class="arrow"/>')
o.append(f'<line x1="225" y1="466" x2="225" y2="550" class="arrow"/>')
o.append(f'<line x1="525" y1="466" x2="525" y2="510" class="conn"/>')
o.append(f'<line x1="490" y1="510" x2="890" y2="510" class="conn"/>')
o.append(f'<line x1="490" y1="510" x2="490" y2="550" class="arrow"/>')
o.append(f'<line x1="690" y1="510" x2="690" y2="550" class="arrow"/>')
o.append(f'<line x1="890" y1="510" x2="890" y2="550" class="arrow"/>')
o.append(f'<path d="M 825 466 L 825 520 L 1155 520 L 1155 550" stroke-dasharray="6 4" stroke="{GREY}" fill="none" marker-end="url(#arrow)"/>')

o.append('<text x="1000" y="512" class="note">advisory</text>')
o.append('<text x="45" y="700" class="note">Lean team (pilot): CEO/COO combined, one support agent, part-time developer, outsourced accounting and legal.</text>')
o.append('<text x="45" y="720" class="note">Moderate team: add an operations lead, second support agent and full-time developer. Ambitious: add finance, marketing and supplier success roles.</text>')
o.append('<text x="45" y="740" class="note">Segregation of duties: the person who approves supplier payouts should not be the only person who reconciles payments.</text>')
svg3 = svg(1360, 780, "\n".join(o))
(OUT / "organisation.svg").write_text(svg3, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4. Technology architecture
# ---------------------------------------------------------------------------
t = []
t.append('<text x="45" y="48" class="title">Proposed technology architecture (MVP first)</text>')
t.append('<text x="45" y="72" class="subtitle">A modular monolith is sufficient for the pilot. Microservices, native apps and AI features are deferred.</text>')

# clients
t.append(box(80, 110, 280, 80, ["CUSTOMER WEB / PWA", "Mobile-first, low-bandwidth, SEO"], "box", "h", "t"))
t.append(box(400, 110, 260, 80, ["SUPPLIER PORTAL", "Listings, stock, orders, payouts"], "box", "h", "t"))
t.append(box(700, 110, 260, 80, ["ADMIN CONSOLE", "Orders, exceptions, refunds, risk"], "box", "h", "t"))
t.append(box(1000, 110, 300, 80, ["SUPPORT & NOTIFICATIONS", "SMS, WhatsApp, email, help desk"], "box", "h", "t"))

# edge
t.append(box(80, 240, 1220, 60, ["EDGE: Cloudflare / WAF · TLS · CDN · rate limiting · bot protection"], "light", "h", "t"))

# app layer
t.append(box(80, 340, 1220, 70, ["NEXT.JS + TYPESCRIPT APPLICATION (SSR, PWA, accessible, Swahili/English)"], "ops", "h", "t"))
t.append(box(80, 440, 1220, 70, ["FASTAPI BACKEND · REST/JSON · authentication · RBAC · business rules · audit log"], "ops", "h", "t"))

# data
t.append(box(80, 550, 280, 100, ["POSTGRESQL", "Orders, catalogue, users, payments, audit"], "box", "h", "t"))
t.append(box(390, 550, 260, 100, ["REDIS (OPTIONAL)", "Sessions, queues, rate limits"], "box", "h", "t"))
t.append(box(680, 550, 280, 100, ["OBJECT STORAGE", "Product images, POD photos, exports"], "box", "h", "t"))
t.append(box(990, 550, 310, 100, ["ANALYTICS & MONITORING", "Events, dashboards, alerts, uptime"], "box", "h", "t"))

# integrations
t.append(box(80, 700, 270, 100, ["PAYMENT GATEWAY", "Licensed PSP: mobile money, cards"], "ext", "h", "t"))
t.append(box(380, 700, 270, 100, ["CARRIER ADAPTER", "Manual console first; API/CSV later"], "ext", "h", "t"))
t.append(box(680, 700, 270, 100, ["MESSAGING", "SMS aggregator, WhatsApp Business"], "ext", "h", "t"))
t.append(box(980, 700, 320, 100, ["IDENTITY & RISK", "Phone OTP, KYC checks, fraud rules"], "ext", "h", "t"))

# arrows
t.append(arrow(220, 190, 220, 240))
t.append(arrow(530, 190, 530, 240))
t.append(arrow(830, 190, 830, 240))
t.append(arrow(1150, 190, 1150, 240))
t.append(arrow(690, 300, 690, 340))
t.append(arrow(690, 410, 690, 440))
for x in (220, 520, 820, 1145):
    t.append(arrow(x, 510, x, 550))
for x in (215, 515, 815, 1140):
    t.append(arrow(x, 650, x, 700))

t.append('<text x="45" y="840" class="note">Deferred: microservices, native iOS/Android apps, automated carrier API, AI recommendations, multi-country, warehouse management, complex escrow.</text>')
svg4 = svg(1380, 870, "\n".join(t))
(OUT / "tech_architecture.svg").write_text(svg4, encoding="utf-8")

print("Generated:", list(p.name for p in OUT.glob("*.svg")))
