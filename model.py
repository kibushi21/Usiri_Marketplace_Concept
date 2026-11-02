"""Financial model for the proposed Usiri-branded marketplace concept.

All figures are planning assumptions in Tanzanian shillings unless stated.
They are illustrative only and must be replaced with quotations before any
investment decision. No franchise fee, logistics rate, or supplier commission
has been quoted by Usiri or any other party.
"""

import json
from pathlib import Path

OUT = Path(__file__).parent / "model_output.json"

# ----------------------------------------------------------------------------
# Core assumptions
# ----------------------------------------------------------------------------
A = {
    "fx_tzs_per_usd": 2645,          # indicative mid-market rate, 28 Oct 2026
    "prelaunch_months": 6,
    "pilot_months": 6,
    "aov": 75_000,
    "commission_rate": 0.08,
    "payment_fee_rate": 0.025,
    "returns_rate": 0.04,
    "refund_handling_rate": 0.01,    # of returned value
    "support_cost_per_order": 700,
    "logistics_fee_per_order": 1_000,
    "logistics_cost_per_order": 500,
    "supplier_subscriptions_month": 600_000,
    "sponsored_revenue_month": 500_000,
    "fixed_opex_moderate": 5_600_000,
    "fixed_opex_lean": 2_200_000,
    "fixed_opex_ambitious": 12_000_000,
    "pilot_target_orders_month6": 900,
    "worked_orders": 1_000,
    "monthly_visits_target": 45_000,
    "conversion_target": 0.02,
    "cac_target": 8_000,
    "repeat_target": 0.20,
}

# ----------------------------------------------------------------------------
# Startup budget (one-time)
# ----------------------------------------------------------------------------
startup_items = [
    ("Company formation, TIN, business licence, basic legal", 1_500_000, 2_500_000, 4_000_000),
    ("Partner/franchise negotiation and legal due diligence", 1_500_000, 5_000_000, 10_000_000),
    ("Illustrative initial brand licence/franchise fee (placeholder)", 0, 15_000_000, 50_000_000),
    ("Brand identity and UI/UX design", 800_000, 2_500_000, 6_000_000),
    ("MVP development (founder time plus contractors)", 6_000_000, 18_000_000, 40_000_000),
    ("Payment gateway integration and testing", 400_000, 1_200_000, 3_000_000),
    ("Devices, office setup and basic equipment", 800_000, 2_500_000, 7_000_000),
    ("Supplier onboarding and catalogue preparation", 800_000, 2_500_000, 6_000_000),
    ("Launch marketing and customer acquisition", 2_000_000, 6_000_000, 15_000_000),
    ("Legal documents: T&Cs, privacy, consumer-contract filing", 800_000, 2_500_000, 5_000_000),
]

startup = []
for name, lean, mod, amb in startup_items:
    startup.append({"item": name, "lean": lean, "moderate": mod, "ambitious": amb})

subtotals = {k: sum(row[k] for row in startup) for k in ("lean", "moderate", "ambitious")}
contingency = {k: round(subtotals[k] * 0.15) for k in subtotals}
one_time_totals = {k: subtotals[k] + contingency[k] for k in subtotals}

# ----------------------------------------------------------------------------
# Monthly operating expenses
# ----------------------------------------------------------------------------
opex_items = [
    ("Founder/management salaries", 0, 1_200_000, 3_900_000),
    ("Customer support and operations staff", 650_000, 1_200_000, 1_400_000),
    ("Development/maintenance contractor", 0, 600_000, 1_400_000),
    ("Cloud hosting, database and CDN", 150_000, 300_000, 500_000),
    ("Domain, email, security and backup tools", 50_000, 100_000, 250_000),
    ("SMS/WhatsApp notifications", 80_000, 150_000, 250_000),
    ("Payment reconciliation and finance tools", 50_000, 80_000, 120_000),
    ("Marketing and customer acquisition", 500_000, 800_000, 2_000_000),
    ("Field transport and supplier visits", 250_000, 300_000, 400_000),
    ("Refund and claims reserve", 200_000, 250_000, 400_000),
    ("Accounting, payroll and legal retainer", 200_000, 300_000, 600_000),
    ("Office or co-working space", 0, 200_000, 600_000),
    ("Miscellaneous", 70_000, 120_000, 180_000),
]
opex = [{"item": n, "lean": l, "moderate": m, "ambitious": a} for n, l, m, a in opex_items]
opex_totals = {k: sum(row[k] for row in opex) for k in ("lean", "moderate", "ambitious")}

# ----------------------------------------------------------------------------
# Unit economics and worked example
# ----------------------------------------------------------------------------
def unit_economics(aov=A["aov"], commission=A["commission_rate"]):
    # Commission and payment fees are earned/charged on net GMV after returns.
    net_gmv = aov * (1 - A["returns_rate"])
    commission_tzs = net_gmv * commission
    payment = net_gmv * A["payment_fee_rate"]
    returns_value = aov * A["returns_rate"]
    refund_handling = returns_value * A["refund_handling_rate"]
    support = A["support_cost_per_order"]
    logistics_net = A["logistics_fee_per_order"] - A["logistics_cost_per_order"]
    contribution = commission_tzs + logistics_net - payment - refund_handling - support
    return {
        "aov": aov,
        "net_gmv": net_gmv,
        "commission_rate": commission,
        "commission_tzs": commission_tzs,
        "payment_fee": payment,
        "refund_handling": refund_handling,
        "support": support,
        "logistics_net": logistics_net,
        "contribution": contribution,
        "contribution_pct_gmv": contribution / aov,
    }

worked = unit_economics()
orders = A["worked_orders"]
gmv = orders * A["aov"]
returns_value = gmv * A["returns_rate"]
net_gmv = gmv - returns_value
revenue_lines = {
    "commission": net_gmv * A["commission_rate"],
    "subscriptions": A["supplier_subscriptions_month"],
    "logistics_coordination": orders * A["logistics_fee_per_order"],
    "sponsored": A["sponsored_revenue_month"],
}
revenue_total = sum(revenue_lines.values())
variable_lines = {
    "payment_fees": net_gmv * A["payment_fee_rate"],
    "refund_handling": returns_value * A["refund_handling_rate"],
    "support": orders * A["support_cost_per_order"],
    "logistics_coordination_cost": orders * A["logistics_cost_per_order"],
}
variable_total = sum(variable_lines.values())
contribution = revenue_total - variable_total
net_result = contribution - A["fixed_opex_moderate"]

revenue_example = {
    "orders": orders,
    "aov": A["aov"],
    "gross_order_value": gmv,
    "returns_value": returns_value,
    "net_gmv": net_gmv,
    "revenue_lines": revenue_lines,
    "revenue_total": revenue_total,
    "variable_lines": variable_lines,
    "variable_total": variable_total,
    "contribution": contribution,
    "fixed_opex": A["fixed_opex_moderate"],
    "net_result": net_result,
    "take_rate_gross": revenue_total / gmv,
    "contribution_margin_gross": contribution / gmv,
    "memo_customer_delivery_fees": orders * 5_000,
    "memo_carrier_charges": orders * 5_000,
    "memo_supplier_goods_value": net_gmv,
}

# ----------------------------------------------------------------------------
# Break-even analysis
# ----------------------------------------------------------------------------
ancillary = A["supplier_subscriptions_month"] + A["sponsored_revenue_month"]

def break_even_orders(aov, commission, fixed):
    ue = unit_economics(aov, commission)
    return (fixed - ancillary) / ue["contribution"], ue

be_base, _ = break_even_orders(A["aov"], A["commission_rate"], A["fixed_opex_moderate"])
be_lean, _ = break_even_orders(A["aov"], A["commission_rate"], A["fixed_opex_lean"])
be_amb, _ = break_even_orders(A["aov"], A["commission_rate"], A["fixed_opex_ambitious"])

aovs = [50_000, 75_000, 100_000]
commissions = [0.06, 0.08, 0.10]
sensitivity = []
for aov in aovs:
    for c in commissions:
        be, ue = break_even_orders(aov, c, A["fixed_opex_moderate"])
        sensitivity.append({
            "aov": aov,
            "commission_rate": c,
            "contribution_per_order": ue["contribution"],
            "break_even_orders": be,
            "orders_per_day": be / 30,
        })

# ----------------------------------------------------------------------------
# 12-month cash plan
# ----------------------------------------------------------------------------
ramp = [100, 250, 450, 650, 800, 900]
subs_ramp = [200_000, 300_000, 400_000, 500_000, 600_000, 600_000]
ads_ramp = {
    "lean": [0, 0, 50_000, 100_000, 150_000, 200_000],
    "moderate": [0, 0, 100_000, 250_000, 400_000, 500_000],
    "ambitious": [0, 0, 200_000, 400_000, 700_000, 900_000],
}

cash_plans = {}
for scenario, fixed in (("lean", A["fixed_opex_lean"]), ("moderate", A["fixed_opex_moderate"]), ("ambitious", A["fixed_opex_ambitious"])):
    monthly = []
    prelaunch = opex_totals[scenario] * A["prelaunch_months"]
    cumulative = -(one_time_totals[scenario] + prelaunch)
    for i, o in enumerate(ramp):
        rev = o * worked["contribution"] + subs_ramp[i] + ads_ramp[scenario][i]
        net = rev - fixed
        cumulative += net
        monthly.append({"month": i + 1, "orders": o, "contribution_and_ancillary": rev, "fixed": fixed, "net": net, "cumulative": cumulative})
    funding = one_time_totals[scenario] + prelaunch - sum(m["net"] for m in monthly)
    cash_plans[scenario] = {
        "monthly": monthly,
        "prelaunch_opex": prelaunch,
        "pilot_net": sum(m["net"] for m in monthly),
        "funding_requirement_before_buffer": funding,
        "buffer_10pct": round(funding * 0.10),
        "funding_requirement_with_buffer": round(funding * 1.10),
    }

# ----------------------------------------------------------------------------
# KPI targets
# ----------------------------------------------------------------------------
kpis = [
    ("Verified suppliers", "Suppliers that passed KYC and have at least one live listing", "40 by month 3; 60 by month 6", "Supplier register", "Weekly"),
    ("Active products", "Listings visible, in stock and not suppressed", "600 by month 3; 1,200 by month 6", "Catalogue", "Weekly"),
    ("Monthly website visitors", "Unique visitors to web/PWA", "45,000 by month 6", "Analytics", "Weekly"),
    ("Conversion rate", "Completed orders / unique visitors", "2.0% by month 6", "Analytics + orders", "Weekly"),
    ("Completed orders", "Orders delivered or collected and confirmed", "900 per month by month 6", "Order system", "Daily"),
    ("Average order value", "Net GMV / completed orders", "TZS 75,000 (range 50,000-100,000)", "Order system", "Weekly"),
    ("Cancellation rate", "Cancelled orders / placed orders", "Below 4%", "Order system", "Weekly"),
    ("Return rate", "Returned units / delivered units", "Below 5% (electronics may be higher)", "Returns log", "Weekly"),
    ("On-time delivery", "Delivered within promised window", "At least 90%", "Carrier manifest + POD", "Weekly"),
    ("Cost per acquired customer", "Marketing spend / first-time buyers", "At most TZS 8,000", "Marketing + orders", "Monthly"),
    ("Repeat purchase rate", "Buyers with 2+ orders in 90 days", "At least 20% by month 6", "Order system", "Monthly"),
    ("Contribution margin", "Contribution / gross order value", "At least 4% by month 6", "Finance", "Monthly"),
    ("Complaints resolved", "Resolved within 48 hours", "At least 90%", "Support system", "Weekly"),
    ("Supplier retention", "Suppliers active after 90 days", "At least 80%", "Supplier register", "Quarterly"),
    ("Platform uptime", "Availability of checkout and order APIs", "At least 99.5% monthly", "Monitoring", "Monthly"),
]

# ----------------------------------------------------------------------------
# Risk register
# ----------------------------------------------------------------------------
risks = [
    ("R01", "Usiri declines the franchise/brand proposal or negotiations stall", "Strategic/partner", 4, 5,
     "Run the project on an independent-brand track in parallel; approach at least two alternative carriers; set a decision deadline before spending on brand-specific assets.", "Founder lead"),
    ("R02", "Supplier fraud, counterfeit goods or misrepresentation", "Commercial/trust", 3, 5,
     "Business verification, physical shop visits, sample checks, category restrictions, supplier warranties, buyer protection reserve, delisting policy.", "COO"),
    ("R03", "Delivery failures, late parcels or damaged goods erode trust", "Operational", 4, 4,
     "Written SLA, two-attempt delivery, collection points, parcel photos, goods-in-transit insurance, exception desk, weekly carrier review.", "Ops lead"),
    ("R04", "Low demand or high customer acquisition cost", "Commercial", 4, 4,
     "Narrow category and geography, pre-launch waiting list, supplier-led demand, referral incentives, stop-loss marketing budget.", "CEO"),
    ("R05", "Thin margins make the model unviable at pilot volume", "Financial", 4, 4,
     "Test 8-12% commission, supplier subscriptions, delivery coordination fee; keep fixed costs lean; break-even sensitivity reviewed monthly.", "Finance lead"),
    ("R06", "Payment fraud, chargebacks or reconciliation gaps", "Financial/technology", 3, 4,
     "Licensed gateway, phone/device checks, velocity limits, order-level reconciliation, hold payouts until delivery confirmation, daily exception queue.", "CTO"),
    ("R07", "Data breach or non-compliance with PDPA 2022", "Legal/technology", 3, 5,
     "Register with PDPC, data map, least-privilege access, encryption, retention policy, breach playbook, cyber insurance, annual review.", "CTO/DPO"),
    ("R08", "Consumer-contract or returns policy challenged by FCC or customers", "Legal/reputation", 3, 3,
     "Plain-language T&Cs, register standard-form contract with FCC, clear returns and refund rules, complaints log, legal review.", "Legal adviser"),
    ("R09", "Jumia or another well-funded marketplace enters or returns", "Competitive", 3, 5,
     "Differentiate on verified suppliers, coordinated delivery and local support; avoid competing on loss-making subsidies; build supplier switching costs.", "CEO"),
    ("R10", "Over-dependence on one logistics partner", "Operational/strategic", 4, 3,
     "Qualify a second carrier before pilot; keep carrier-agnostic adapter layer; standardise SLAs and parcel IDs.", "Ops lead"),
    ("R11", "Key-person dependency and unclear founder roles", "Organisational", 4, 3,
     "Written roles, equity and vesting agreement, documented processes, cross-training, IP assignment to the company.", "Founders"),
    ("R12", "Technology outage or security incident during peak", "Technology", 3, 4,
     "Managed hosting, backups tested quarterly, monitoring and alerts, status page, incident runbook, WAF and rate limiting.", "CTO"),
    ("R13", "Regulatory change or new tax/e-commerce rules", "Regulatory", 3, 3,
     "Quarterly legal/regulatory review, accountant on retainer, flexible contract terms, compliance calendar.", "Legal adviser"),
    ("R14", "Currency or inflation pressure on costs and prices", "Financial", 3, 3,
     "TZS-denominated pricing, periodic repricing, cost buffers, avoid USD-linked fixed commitments where possible.", "Finance lead"),
    ("R15", "Brand or reputational damage from a supplier or delivery incident", "Reputation", 2, 5,
     "Brand-use guidelines, rapid response protocol, compensation policy, transparency report, escalation to brand owner.", "CEO"),
]

# ----------------------------------------------------------------------------
# Decision matrix
# ----------------------------------------------------------------------------
decision_criteria = [
    ("Commercial attractiveness", 0.25, "Size and urgency of customer problem; willingness to pay; competitive intensity"),
    ("Feasibility", 0.20, "Can the team build and operate the MVP with available skills and partners?"),
    ("Cost and funding", 0.15, "Affordable within the group's means; credible path to break-even"),
    ("Risk", 0.20, "Downside exposure, partner dependence, regulatory and trust risk"),
    ("Strategic fit", 0.10, "Fit with founders' skills, network and long-term ambitions"),
    ("Evidence quality", 0.10, "Strength of interview, survey and quotation evidence before committing"),
]

# ----------------------------------------------------------------------------
# Roadmap
# ----------------------------------------------------------------------------
roadmap = [
    ("1. Internal concept review", "2-4 weeks", "Concept document, meeting decision, written go/revise/stop decision", "TZS 0-500k", "Founder availability", "Group agrees to fund Phase 2"),
    ("2. Customer, supplier and competitor research", "6-8 weeks", "30 customer interviews, 15 supplier interviews, 8 mystery shops, competitor price check, survey of 150+ respondents", "TZS 2-5m", "Access to suppliers and customers", "Evidence supports a specific segment and value proposition"),
    ("3. Partner and franchise feasibility", "4-6 weeks", "Carrier capability assessment, draft term sheet, indicative logistics rates, franchise/legal briefing", "TZS 1-3m", "Willingness of carriers to meet", "A carrier confirms interest in a pilot and rates are workable"),
    ("4. Commercial negotiation and legal review", "6-10 weeks", "Heads of terms, brand licence/franchise draft, SLA, data-processing agreement, legal opinion", "TZS 3-8m", "Partner interest; legal counsel", "Terms are affordable and risk allocation is acceptable"),
    ("5. MVP build and operational preparation", "8-12 weeks", "Working MVP, supplier handbook, support scripts, finance controls, pilot plan", "TZS 10-30m", "Phase 2-4 findings; team capacity", "MVP passes acceptance tests and 20 suppliers are ready"),
    ("6. Controlled pilot", "12 weeks", "Live orders in one city and selected corridors; weekly dashboard; incident log", "TZS 8-20m", "MVP, suppliers, carrier, payment gateway", "KPIs meet agreed thresholds or a clear fix path exists"),
    ("7. Evaluation and expansion decision", "4 weeks", "Pilot report, unit economics, decision memo, next-phase budget", "TZS 1-2m", "Pilot data", "Group decides to scale, pivot or stop"),
]

# ----------------------------------------------------------------------------
# Sources
# ----------------------------------------------------------------------------
sources = [
    ("Usiri Group of Companies", "About", "https://www.usirigroup.co.tz/about", "29 Oct 2026", "Self-reported services, routes, years, customer count", "Company marketing; figures inconsistent across pages"),
    ("Usiri Group of Companies", "Transportation", "https://www.usirigroup.co.tz/services/transportation", "29 Oct 2026", "Carriage of goods, parcels, luggage and freight; route list", "No API or rate card published"),
    ("Usiri Group of Companies", "Locations", "https://www.usirigroup.co.tz/locations", "29 Oct 2026", "Branch/office list across Dar es Salaam and upcountry", "Self-reported"),
    ("Usiri Group of Companies", "Tracking link", "https://www.usirigroup.co.tz/track", "29 Oct 2026", "Link returned HTTP 404 during review", "Indicates no public tracking interface at time of review"),
    ("TCRA", "Communications Statistics Report, quarter ending March 2025", "https://www.tcra.go.tz/tcra-tovuti/2025/mamlaka-website/documents/quarterly-statistics/Communication_Statistics_report_for_end_of_March_2025_1744814447_4329fbf17d.pdf", "29 Oct 2026", "Internet subscriptions 49.3m; mobile money accounts 66.5m; smartphone penetration 35.29%; 4G coverage 91%; courier volumes", "Official statistics; Q1 2025"),
    ("Bank of Tanzania", "National Payment Systems Annual Report 2025", "https://www.bot.go.tz/Publications/Regular/Annual%20Report/en/2026060211494565.pdf", "29 Oct 2026", "75.78m active mobile money users; 2.79m merchants; P2B 2.30bn transactions worth TZS 37.5trn; 72 licensed non-bank providers", "Official; 2025 data"),
    ("International Trade Administration (USA)", "Tanzania Country Commercial Guide - eCommerce", "https://www.trade.gov/country-commercial-guides/tanzania-ecommerce", "29 Oct 2026", "Most online buying via social media; 2025 market estimate USD 693.11m, 7% growth; Facebook/Instagram user estimates", "Government guide; market estimate is third-party and differs from other estimates"),
    ("eCommerceDB", "E-Commerce Industry in Tanzania", "https://ecdb.com/resources/sample-data/market/tz/all", "29 Oct 2026", "Alternative 2025 market estimate of USD 536m and 15-20% growth", "Model-based estimate; conflicts with trade.gov figure"),
    ("Reuters / Africanews", "Jumia closes Tanzania operations", "https://www.africanews.com/2019/12/03/how-jumia-closed-two-portfolios-in-10-days-from-cameroon-to-tanzania/", "29 Oct 2026", "Jumia ceased Tanzanian e-commerce operations on 27 November 2019", "Historical reporting"),
    ("TechCabal", "Jumia considers Tanzania and Angola expansion", "https://techcabal.com/2025/11/18/jumia-considers-tanzania-angola-expansion/", "29 Oct 2026", "Jumia was considering Tanzania as a potential new market; no launch confirmed", "News report; no confirmed date"),
    ("TRA", "Value Added Tax", "https://www.tra.go.tz/page/value-added-tax-vat", "29 Oct 2026", "VAT rate 18%; registration threshold TZS 200m (or TZS 100m in six months)", "Official tax guidance; confirm with accountant"),
    ("PwC", "Tanzania - Corporate - Taxes on corporate income", "https://taxsummaries.pwc.com/tanzania/corporate/taxes-on-corporate-income", "29 Oct 2026", "Corporate income tax 30% for resident companies", "Professional summary; confirm current Finance Act"),
    ("ZATRA", "Franchising Tanzania: Law, Tax and Royalty Guide", "https://www.zatra.co/post/franchising-tanzania", "29 Oct 2026", "No franchise Act; Law of Contract Act Cap. 345; Trade and Service Marks Act Cap. 326; 15% withholding on non-resident royalties", "Law-firm commentary; not legal advice"),
    ("DLA Piper", "Data protection laws in Tanzania", "https://www.dlapiperdataprotection.com/?c=TZ&t=l", "29 Oct 2026", "PDPA 2022 obligations; PDPC registration; penalties up to TZS 5bn or 10 years", "Professional summary; verify against the Act"),
    ("Rex Attorneys", "PDPC registration deadline", "https://rexattorneys.co.tz/portfolio/reminder-to-clients-final-deadline-for-registration-with-the-personal-data-protection-commission-pdpc/", "29 Oct 2026", "Registration deadline 8 April 2026; enforcement from 9 April 2026; DPO required", "Law-firm update; confirm with PDPC"),
    ("Fair Competition Commission", "Standard Form (Consumer Contracts) Regulations 2014", "https://www.fcc.go.tz/attachments/attachment-1719186970334-2762257834.%20Standard%20Form%20CONSUMER%20CONTRACTS%20Regulations%202014.pdf", "29 Oct 2026", "Standard-form consumer contracts must be registered with FCC; application within 21 days; FCC review", "Regulation; confirm filing practice"),
    ("TCRA", "Postal services and licensing", "https://www.tcra.go.tz/resources/postal-services", "29 Oct 2026", "Courier licence categories and fees (application TZS 60,000; initial up to TZS 18m)", "Official; confirm applicability to marketplace model"),
    ("TCRA", "National Addressing and Postcode", "https://www.tcra.go.tz/services/featured/national-adressing-and-postcode", "29 Oct 2026", "Five-digit postcode system and national addressing programme", "Official; address quality remains a practical constraint"),
    ("Electronic Transactions Act 2015 (Cap. 442 R.E. 2022)", "Ministry of Finance", "https://www.mof.go.tz/uploads/documents/en-1676545044-THE%20ELECTRONIC%20TRANSACTIONS%20ACT,%20CAP%20442%20R.E.%202022.pdf", "29 Oct 2026", "Legal recognition of electronic transactions, signatures and records", "Primary legislation"),
]

# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
output = {
    "assumptions": A,
    "startup_items": startup,
    "startup_subtotals": subtotals,
    "startup_contingency": contingency,
    "startup_totals": one_time_totals,
    "opex_items": opex,
    "opex_totals": opex_totals,
    "unit_economics": worked,
    "revenue_example": revenue_example,
    "break_even": {
        "lean": be_lean,
        "moderate": be_base,
        "ambitious": be_amb,
        "ancillary": ancillary,
        "sensitivity": sensitivity,
    },
    "cash_plans": cash_plans,
    "kpis": kpis,
    "risks": risks,
    "decision_criteria": decision_criteria,
    "roadmap": roadmap,
    "sources": sources,
}

OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
print(f"Wrote {OUT}")
print(f"Startup totals: {one_time_totals}")
print(f"Opex totals: {opex_totals}")
print(f"Contribution/order: {worked['contribution']:,.0f}")
print(f"Break-even orders/month: lean={be_lean:,.0f}, moderate={be_base:,.0f}, ambitious={be_amb:,.0f}")
print(f"Worked example net: {net_result:,.0f}")
for k, v in cash_plans.items():
    print(k, "funding requirement:", f"{v['funding_requirement_with_buffer']:,.0f}")
