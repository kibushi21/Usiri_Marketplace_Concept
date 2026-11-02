"""Build the startup budget, break-even and decision workbook."""

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule

BASE = Path(__file__).parent
DATA = json.loads((BASE / "model_output.json").read_text(encoding="utf-8"))
OUT = BASE / "Startup_Budget_and_Decision_Workbook.xlsx"

NAVY = "1F3A5F"
TEAL = "2A7F7F"
AMBER = "C8892A"
LIGHT = "F2F5F9"
PALE_BLUE = "E4EDF7"
PALE_TEAL = "E3F0EE"
PALE_AMBER = "FBEFD8"
WHITE = "FFFFFF"
GREY = "5A6572"
BORDER_CLR = "D8E0E8"

thin = Side(style="thin", color=BORDER_CLR)
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

TITLE_FONT = Font(name="Calibri", size=18, bold=True, color=WHITE)
SUBTITLE_FONT = Font(name="Calibri", size=10.5, italic=True, color=GREY)
SECTION_FONT = Font(name="Calibri", size=12, bold=True, color=WHITE)
HEADER_FONT = Font(name="Calibri", size=10.5, bold=True, color=WHITE)
BODY_FONT = Font(name="Calibri", size=10.5, color="222222")
BOLD_FONT = Font(name="Calibri", size=10.5, bold=True, color="222222")
NOTE_FONT = Font(name="Calibri", size=9.5, italic=True, color=GREY)
LINK_FONT = Font(name="Calibri", size=9.5, color="0563C1", underline="single")

TITLE_FILL = PatternFill("solid", fgColor=NAVY)
SECTION_FILL = PatternFill("solid", fgColor=TEAL)
HEADER_FILL = PatternFill("solid", fgColor=NAVY)
LIGHT_FILL = PatternFill("solid", fgColor=LIGHT)
PALE_BLUE_FILL = PatternFill("solid", fgColor=PALE_BLUE)
PALE_TEAL_FILL = PatternFill("solid", fgColor=PALE_TEAL)
PALE_AMBER_FILL = PatternFill("solid", fgColor=PALE_AMBER)
INPUT_FILL = PatternFill("solid", fgColor="FFF7DE")

WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)

TZS = '#,##0'
PCT = '0.0%'


def sheet_title(ws, title, subtitle, last_col=6):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    c = ws.cell(row=1, column=1, value=title)
    c.font = TITLE_FONT
    c.fill = TITLE_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 34
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    c = ws.cell(row=2, column=1, value=subtitle)
    c.font = SUBTITLE_FONT
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 30
    ws.sheet_view.showGridLines = False


def section(ws, row, text, last_col=6):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=1, value=text)
    c.font = SECTION_FONT
    c.fill = SECTION_FILL
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 22
    return row + 1


def header_row(ws, row, headers, widths=None):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = CENTER
        c.border = BORDER
    ws.row_dimensions[row].height = 30
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    return row + 1


def body_row(ws, row, values, fills=None, fonts=None, formats=None, aligns=None, height=None):
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = (fonts[i-1] if fonts and fonts[i-1] else BODY_FONT)
        c.alignment = (aligns[i-1] if aligns and aligns[i-1] else LEFT)
        c.border = BORDER
        if fills and fills[i-1]:
            c.fill = fills[i-1]
        if formats and formats[i-1]:
            c.number_format = formats[i-1]
    if height:
        ws.row_dimensions[row].height = height
    return row + 1


def note(ws, row, text, last_col=6, height=28):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    c = ws.cell(row=row, column=1, value=text)
    c.font = NOTE_FONT
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.row_dimensions[row].height = height
    return row + 1


wb = Workbook()

# ===========================================================================
# READ ME
# ===========================================================================
ws = wb.active
ws.title = "Read Me"
sheet_title(ws, "Proposed multi-vendor marketplace — startup budget and decision workbook",
            "Working name: Usiri Marketplace. Concept-stage planning tool. Not an approved project, franchise, partnership or investment case.", 6)
widths = [4, 34, 18, 18, 22, 52]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

r = 4
r = section(ws, r, "Purpose", 6)
r = note(ws, r, "This workbook supports the internal discussion of a proposed multi-vendor e-commerce marketplace in Tanzania, potentially operating under a brand licence or franchise from Usiri Group of Companies and using contracted transport capacity. It provides illustrative startup costs, operating expenses, unit economics, break-even thresholds, KPI targets, a risk register, a decision matrix and a phased roadmap.", 6)
r = note(ws, r, "Every figure is an assumption for planning, not a quotation. No franchise fee, royalty rate, logistics price, commission rate, supplier commitment or funding commitment has been obtained from Usiri or any other party.", 6)
r += 1

r = section(ws, r, "How to use this workbook", 6)
steps = [
    ("1", "Read the Assumptions sheet first.", "It is a register of what the model assumes and what evidence is missing, not a live model. Revise it only after obtaining quotes, interviews or legal advice."),
    ("2", "Review the Startup Budget and Monthly Opex sheets.", "They show lean, moderate and ambitious scenarios. One-time costs are separated from recurring costs."),
    ("3", "Use the What-if calculator on the Break-even sheet.", "Pale-yellow cells are live inputs. Change AOV, commission, fees, returns or fixed costs and the output rows recalculate. The other sheets are a static snapshot of the base model."),
    ("4", "Score the project on the Decision Matrix.", "Each founder scores independently before the group discussion, then the group reconciles differences."),
    ("5", "Use the Risk Register and Roadmap as living documents.", "Assign an owner and review monthly; update the register after each phase."),
]
for n, a, b in steps:
    ws.cell(row=r, column=1, value=n).font = BOLD_FONT
    ws.cell(row=r, column=1).alignment = CENTER
    ws.cell(row=r, column=2, value=a).font = BOLD_FONT
    ws.cell(row=r, column=2).alignment = LEFT
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
    c = ws.cell(row=r, column=4, value=b)
    c.font = BODY_FONT
    c.alignment = LEFT
    ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6)
    ws.row_dimensions[r].height = max(30, 14 * (len(b) // 88 + 1))
    r += 1
r += 1

r = section(ws, r, "Key figures at a glance", 6)
r = header_row(ws, r, ["", "Metric", "Value", "Unit", "Basis", "Interpretation"], None)
key_rows = [
    ("Contribution per order", DATA["unit_economics"]["contribution"], "TZS", "AOV TZS 75,000; 8% commission; 4% returns", "Before fixed costs and ancillary revenue"),
    ("Break-even volume (moderate)", DATA["break_even"]["moderate"], "orders/month", "Fixed opex TZS 5.6m; ancillary TZS 1.1m", "About {:.0f} orders per day".format(DATA["break_even"]["moderate"]/30)),
    ("Break-even volume (lean)", DATA["break_even"]["lean"], "orders/month", "Fixed opex TZS 2.2m", "About {:.0f} orders per day".format(DATA["break_even"]["lean"]/30)),
    ("Moderate 12-month funding need", DATA["cash_plans"]["moderate"]["funding_requirement_with_buffer"], "TZS", "One-time + 6 months pre-launch + 6 months pilot + 10% buffer", "Includes a placeholder franchise fee; exclude if none is agreed"),
    ("Lean 12-month funding need", DATA["cash_plans"]["lean"]["funding_requirement_with_buffer"], "TZS", "Same structure", "Assumes founders take no salary"),
]
for label, val, unit, basis, interp in key_rows:
    r = body_row(ws, r, ["", label, val, unit, basis, interp],
                 formats=[None, None, TZS if unit == "TZS" else '#,##0', None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=30)
r += 1

r = section(ws, r, "Important limitations", 6)
lims = [
    "Market size figures in circulation differ widely. This pack cites two estimates and treats both as directional, not as a forecast.",
    "Usiri's route count, customer numbers and service claims are self-reported and inconsistent across its own pages. They must be verified in writing.",
    "No public Usiri API, rate card or tracking interface was found. The pilot assumes manual coordination.",
    "Tax, franchise, payment, consumer-protection and data-protection positions must be confirmed by a Tanzanian lawyer and accountant.",
    "The model excludes founder living costs, financing costs, inflation, currency depreciation and any marketing beyond the stated budget.",
    "The model assumes a single-city pilot with doorstep delivery and collection-point fallback, not nationwide delivery.",
]
for lim in lims:
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    c = ws.cell(row=r, column=2, value="•  " + lim)
    c.font = BODY_FONT
    c.alignment = LEFT
    ws.row_dimensions[r].height = 28
    r += 1
r += 1
r = note(ws, r, "Prepared 29 October 2026. Currency: Tanzanian shillings (TZS). Indicative exchange rate used only for context: TZS 2,645 = USD 1.", 6)

# ===========================================================================
# ASSUMPTIONS
# ===========================================================================
ws = wb.create_sheet("Assumptions")
sheet_title(ws, "Assumptions register", "Every downstream figure depends on these inputs. Replace with evidence before committing funds.", 6)
r = 4
r = section(ws, r, "Commercial assumptions", 6)
r = header_row(ws, r, ["#", "Assumption", "Value", "Unit", "Basis / source", "Evidence needed"], [4, 38, 16, 14, 48, 46])

assumptions_rows = [
    ("A1", "Pilot city", "Dar es Salaam", "—", "Largest population and supplier concentration; 5.38m residents (2022 census)", "Supplier and customer interviews"),
    ("A2", "Pilot duration", DATA["assumptions"]["pilot_months"], "months", "Planning assumption", "Team capacity and funding"),
    ("A3", "Average order value (AOV)", DATA["assumptions"]["aov"], "TZS", "Planning assumption for electronics/accessories mix", "Competitor price checks and pre-orders"),
    ("A4", "Commission rate", DATA["assumptions"]["commission_rate"], "of net GMV", "Planning assumption; test 6-12%", "Supplier willingness-to-pay interviews"),
    ("A5", "Payment processing fee", DATA["assumptions"]["payment_fee_rate"], "of net GMV", "Typical gateway range 0-3.5% for mobile money; cards higher", "Written gateway quotation"),
    ("A6", "Return rate", DATA["assumptions"]["returns_rate"], "of GMV", "Planning assumption; electronics can be higher", "Pilot data and competitor policy review"),
    ("A7", "Refund handling cost", DATA["assumptions"]["refund_handling_rate"], "of returned value", "Inspection, repackaging, reverse transport", "Carrier quotation"),
    ("A8", "Variable support cost", DATA["assumptions"]["support_cost_per_order"], "TZS/order", "Staff time per order at pilot volume", "Time-and-motion study"),
    ("A9", "Logistics coordination fee", DATA["assumptions"]["logistics_fee_per_order"], "TZS/order", "Charged to supplier; not the carrier charge", "Supplier interviews"),
    ("A10", "Logistics coordination cost", DATA["assumptions"]["logistics_cost_per_order"], "TZS/order", "Admin time to book and monitor shipments", "Operations estimate"),
    ("A11", "Supplier subscriptions", DATA["assumptions"]["supplier_subscriptions_month"], "TZS/month", "20 paying suppliers at TZS 30,000", "Supplier interviews"),
    ("A12", "Sponsored placements", DATA["assumptions"]["sponsored_revenue_month"], "TZS/month", "Only after traffic is demonstrated", "Advertiser interest"),
    ("A13", "Fixed opex (moderate)", DATA["assumptions"]["fixed_opex_moderate"], "TZS/month", "See Monthly Opex", "Quotations and salary benchmarks"),
    ("A14", "Pilot target orders (month 6)", DATA["assumptions"]["pilot_target_orders_month6"], "orders/month", "About 30 per day", "Pre-launch demand test"),
    ("A15", "Monthly visitors (month 6)", DATA["assumptions"]["monthly_visits_target"], "visits", "2.0% conversion to 900 orders", "Marketing plan"),
    ("A16", "Customer acquisition cost target", DATA["assumptions"]["cac_target"], "TZS/new customer", "Assumes TZS 800k marketing / 160 new buyers", "Campaign tests"),
    ("A17", "Repeat purchase target", DATA["assumptions"]["repeat_target"], "of buyers in 90 days", "Planning hypothesis", "Cohort tracking"),
    ("A18", "Exchange rate (context only)", DATA["assumptions"]["fx_tzs_per_usd"], "TZS/USD", "Indicative mid-market rate, 28 Oct 2026", "BoT daily rate"),
]
for code, name, val, unit, basis, evidence in assumptions_rows:
    fmt = TZS if unit.startswith("TZS") else (PCT if unit.startswith("of") else '#,##0')
    r = body_row(ws, r, [code, name, val, unit, basis, evidence],
                 formats=[None, None, fmt, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=32)

r += 1
r = section(ws, r, "What is deliberately not assumed", 6)
not_assumed = [
    "No franchise fee, royalty rate, territory or exclusivity has been agreed or quoted. The budget uses a placeholder only in the moderate and ambitious scenarios.",
    "No logistics rate card, service-level agreement, API access or tracking integration has been confirmed by Usiri.",
    "No supplier has committed to list, no customer has committed to buy, and no payment provider has approved the merchant account.",
    "No regulatory approval, tax ruling or legal opinion has been obtained.",
]
for x in not_assumed:
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    c = ws.cell(row=r, column=2, value="•  " + x)
    c.font = BODY_FONT
    c.alignment = LEFT
    ws.row_dimensions[r].height = 26
    r += 1

# ===========================================================================
# STARTUP BUDGET
# ===========================================================================
ws = wb.create_sheet("Startup Budget")
sheet_title(ws, "Illustrative startup budget (TZS)", "One-time costs, pre-launch operating costs and 12-month funding requirement. All figures are planning estimates.", 6)
r = 4
r = section(ws, r, "One-time setup costs", 6)
r = header_row(ws, r, ["#", "Cost item", "Lean", "Moderate", "Ambitious", "Notes / validation"], [4, 44, 16, 16, 16, 50])
startup_notes = {
    "Company formation, TIN, business licence, basic legal": "BRELA, TRA and local government; confirm current fees",
    "Partner/franchise negotiation and legal due diligence": "Legal fees only; excludes any franchise fee",
    "Illustrative initial brand licence/franchise fee (placeholder)": "PLACEHOLDER ONLY — no fee has been quoted",
    "Brand identity and UI/UX design": "May be done in-house at lean end",
    "MVP development (founder time plus contractors)": "Largest line; obtain two written development quotes",
    "Payment gateway integration and testing": "Setup and certification; exclude per-transaction fees",
    "Devices, office setup and basic equipment": "Laptops, phones, furniture; lean assumes remote",
    "Supplier onboarding and catalogue preparation": "Photography, training, verification visits",
    "Launch marketing and customer acquisition": "Pilot campaign; stop-loss budget",
    "Legal documents: T&Cs, privacy, consumer-contract filing": "FCC standard-form filing, PDPA documents",
}
for i, row in enumerate(DATA["startup_items"], 1):
    r = body_row(ws, r, [f"S{i:02d}", row["item"], row["lean"], row["moderate"], row["ambitious"],
                         startup_notes.get(row["item"], "")],
                 formats=[None, None, TZS, TZS, TZS, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=32)
r = body_row(ws, r, ["", "Subtotal", DATA["startup_subtotals"]["lean"], DATA["startup_subtotals"]["moderate"], DATA["startup_subtotals"]["ambitious"], ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_BLUE_FILL, PALE_BLUE_FILL, PALE_BLUE_FILL, PALE_BLUE_FILL, None],
             formats=[None, None, TZS, TZS, TZS, None], aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=24)
r = body_row(ws, r, ["", "Contingency (15%)", DATA["startup_contingency"]["lean"], DATA["startup_contingency"]["moderate"], DATA["startup_contingency"]["ambitious"], "For scope and price uncertainty"],
             formats=[None, None, TZS, TZS, TZS, None], aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=24)
r = body_row(ws, r, ["", "Total one-time setup", DATA["startup_totals"]["lean"], DATA["startup_totals"]["moderate"], DATA["startup_totals"]["ambitious"], ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, TZS, TZS, TZS, None], aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=26)
r += 1

r = section(ws, r, "Pre-launch and 12-month funding requirement", 6)
r = header_row(ws, r, ["", "Item", "Lean", "Moderate", "Ambitious", "Notes"], None)
pre_rows = [
    ("Pre-launch operating costs (6 months)", DATA["cash_plans"]["lean"]["prelaunch_opex"], DATA["cash_plans"]["moderate"]["prelaunch_opex"], DATA["cash_plans"]["ambitious"]["prelaunch_opex"], "See Monthly Opex"),
    ("Pilot operating result (6 months)", DATA["cash_plans"]["lean"]["pilot_net"], DATA["cash_plans"]["moderate"]["pilot_net"], DATA["cash_plans"]["ambitious"]["pilot_net"], "Negative means cash consumed"),
    ("Funding requirement before buffer", DATA["cash_plans"]["lean"]["funding_requirement_before_buffer"], DATA["cash_plans"]["moderate"]["funding_requirement_before_buffer"], DATA["cash_plans"]["ambitious"]["funding_requirement_before_buffer"], "One-time + pre-launch + pilot result"),
    ("Buffer (10%)", DATA["cash_plans"]["lean"]["buffer_10pct"], DATA["cash_plans"]["moderate"]["buffer_10pct"], DATA["cash_plans"]["ambitious"]["buffer_10pct"], "For delays and cost overruns"),
    ("Total 12-month funding requirement", DATA["cash_plans"]["lean"]["funding_requirement_with_buffer"], DATA["cash_plans"]["moderate"]["funding_requirement_with_buffer"], DATA["cash_plans"]["ambitious"]["funding_requirement_with_buffer"], "Indicative ask; exclude placeholder franchise fee if not applicable"),
]
for label, l, m, a, n in pre_rows:
    bold = label.startswith("Total")
    r = body_row(ws, r, ["", label, l, m, a, n],
                 fonts=[None, BOLD_FONT if bold else BODY_FONT, BOLD_FONT if bold else BODY_FONT, BOLD_FONT if bold else BODY_FONT, BOLD_FONT if bold else BODY_FONT, None],
                 fills=[None, PALE_TEAL_FILL if bold else None, PALE_TEAL_FILL if bold else None, PALE_TEAL_FILL if bold else None, PALE_TEAL_FILL if bold else None, None],
                 formats=[None, None, TZS, TZS, TZS, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=26)
r += 1
r = note(ws, r, "The lean scenario assumes founders take no salary and work from home. The moderate and ambitious scenarios include staff costs. None of the scenarios includes founders' personal living costs, loan interest, inflation or exchange-rate losses.", 6)
r = note(ws, r, "The moderate and ambitious scenarios include a TZS 15m / TZS 50m placeholder for an initial brand licence or franchise fee. This is not a quotation. If no fee is agreed, subtract it from the total.", 6)

# ===========================================================================
# MONTHLY OPEX
# ===========================================================================
ws = wb.create_sheet("Monthly Opex")
sheet_title(ws, "Recurring monthly operating expenses (TZS)", "Steady-state pilot costs. Adjust after quotations and after the pilot team is defined.", 6)
r = 4
r = section(ws, r, "Monthly operating expenses", 6)
r = header_row(ws, r, ["#", "Cost item", "Lean", "Moderate", "Ambitious", "Notes"], [4, 44, 16, 16, 16, 50])
opex_notes = {
    "Founder/management salaries": "Lean assumes unpaid founders; include living costs separately",
    "Customer support and operations staff": "Swahili/English support, order admin",
    "Development/maintenance contractor": "Bug fixes, small features, integrations",
    "Cloud hosting, database and CDN": "Obtain quotations from two providers",
    "Domain, email, security and backup tools": "WAF, monitoring, backups, email",
    "SMS/WhatsApp notifications": "Order and delivery updates",
    "Payment reconciliation and finance tools": "May be manual at lean end",
    "Marketing and customer acquisition": "Stop-loss budget; measure CAC weekly",
    "Field transport and supplier visits": "Supplier verification and pickup coordination",
    "Refund and claims reserve": "Provision, not a bank balance",
    "Accounting, payroll and legal retainer": "Monthly bookkeeping and advice",
    "Office or co-working space": "Lean assumes remote",
    "Miscellaneous": "10% of other lines",
}
for i, row in enumerate(DATA["opex_items"], 1):
    r = body_row(ws, r, [f"O{i:02d}", row["item"], row["lean"], row["moderate"], row["ambitious"], opex_notes.get(row["item"], "")],
                 formats=[None, None, TZS, TZS, TZS, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=30)
r = body_row(ws, r, ["", "Total monthly operating expenses", DATA["opex_totals"]["lean"], DATA["opex_totals"]["moderate"], DATA["opex_totals"]["ambitious"], ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, TZS, TZS, TZS, None], aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=26)
r += 1
r = note(ws, r, "These are planning estimates, not quotations. The largest uncertainties are salaries, marketing efficiency and the cost of customer support per order.", 6)

# ===========================================================================
# REVENUE EXAMPLE
# ===========================================================================
ws = wb.create_sheet("Revenue Example")
sheet_title(ws, "Illustrative monthly revenue and result", "One month at 1,000 completed orders. Shows the difference between GMV, marketplace revenue and operating result.", 6)
r = 4
r = section(ws, r, "Order and GMV build-up", 6)
r = header_row(ws, r, ["", "Line", "Value", "Unit", "Formula / note", ""], [4, 46, 18, 14, 56, 2])
ex = DATA["revenue_example"]
build = [
    ("Completed orders", ex["orders"], "orders", "Pilot target for a strong month"),
    ("Average order value", ex["aov"], "TZS", "Assumption A3"),
    ("Gross order value (GMV)", ex["gross_order_value"], "TZS", "Orders × AOV"),
    ("Returns value", ex["returns_value"], "TZS", "4% of GMV"),
    ("Net GMV", ex["net_gmv"], "TZS", "GMV − returns"),
]
for label, val, unit, formula in build:
    bold = label in ("Gross order value (GMV)", "Net GMV")
    r = body_row(ws, r, ["", label, val, unit, formula, ""],
                 fonts=[None, BOLD_FONT if bold else BODY_FONT, BOLD_FONT if bold else BODY_FONT, BODY_FONT, BODY_FONT, None],
                 formats=[None, None, TZS if unit == "TZS" else '#,##0', None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)

r += 1
r = section(ws, r, "Marketplace revenue", 6)
r = header_row(ws, r, ["", "Revenue line", "Amount", "Unit", "Who pays / when", ""], None)
rev = [
    ("Commission on completed sales", ex["revenue_lines"]["commission"], "TZS", "Supplier; deducted at settlement"),
    ("Supplier subscriptions", ex["revenue_lines"]["subscriptions"], "TZS", "20 suppliers × TZS 30,000/month"),
    ("Logistics coordination fees", ex["revenue_lines"]["logistics_coordination"], "TZS", "Supplier; TZS 1,000/order"),
    ("Sponsored placements", ex["revenue_lines"]["sponsored"], "TZS", "Supplier or brand; monthly"),
]
for label, val, unit, who in rev:
    r = body_row(ws, r, ["", label, val, unit, who, ""],
                 formats=[None, None, TZS, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r = body_row(ws, r, ["", "Total marketplace revenue", ex["revenue_total"], "TZS", "Not equal to GMV", ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, TZS, None, None, None], aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=26)

r += 1
r = section(ws, r, "Variable costs and result", 6)
r = header_row(ws, r, ["", "Line", "Amount", "Unit", "Formula / note", ""], None)
var = [
    ("Payment processing fees", ex["variable_lines"]["payment_fees"], "TZS", "2.5% of net GMV"),
    ("Refund handling", ex["variable_lines"]["refund_handling"], "TZS", "1% of returned value"),
    ("Customer support (variable)", ex["variable_lines"]["support"], "TZS", "TZS 700/order"),
    ("Logistics coordination cost", ex["variable_lines"]["logistics_coordination_cost"], "TZS", "TZS 500/order"),
]
for label, val, unit, formula in var:
    r = body_row(ws, r, ["", label, val, unit, formula, ""],
                 formats=[None, None, TZS, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r = body_row(ws, r, ["", "Total variable costs", ex["variable_total"], "TZS", "", ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, None, None],
             fills=[None, PALE_BLUE_FILL, PALE_BLUE_FILL, PALE_BLUE_FILL, PALE_BLUE_FILL, None],
             formats=[None, None, TZS, None, None, None], aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r = body_row(ws, r, ["", "Contribution before fixed costs", ex["contribution"], "TZS", "Revenue − variable costs", ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, TZS, None, None, None], aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=26)
r = body_row(ws, r, ["", "Fixed monthly operating expenses", ex["fixed_opex"], "TZS", "Moderate scenario", ""],
             formats=[None, None, TZS, None, None, None], aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r = body_row(ws, r, ["", "Net operating result", ex["net_result"], "TZS", "Negative at 1,000 orders/month", ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_AMBER_FILL, PALE_AMBER_FILL, PALE_AMBER_FILL, PALE_AMBER_FILL, None],
             formats=[None, None, TZS, None, None, None], aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=28)

r += 1
r = section(ws, r, "Ratios and memo items", 6)
r = header_row(ws, r, ["", "Metric", "Value", "Unit", "Note", ""], None)
ratios = [
    ("Gross take rate", ex["take_rate_gross"], "% of GMV", "Marketplace revenue / gross order value"),
    ("Contribution margin", ex["contribution_margin_gross"], "% of GMV", "Contribution / gross order value"),
    ("Net operating margin", ex["net_result"]/ex["gross_order_value"], "% of GMV", "Net result / gross order value"),
    ("Customer-paid delivery fees (memo)", ex["memo_customer_delivery_fees"], "TZS", "Pass-through; not marketplace revenue"),
    ("Carrier charges (memo)", ex["memo_carrier_charges"], "TZS", "Pass-through; not a marketplace cost in this model"),
    ("Supplier goods value (memo)", ex["memo_supplier_goods_value"], "TZS", "Belongs to suppliers; not marketplace revenue"),
]
for label, val, unit, n in ratios:
    fmt = PCT if unit.startswith("%") else TZS
    r = body_row(ws, r, ["", label, val, unit, n, ""],
                 formats=[None, None, fmt, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r += 1
r = note(ws, r, "The example deliberately shows a loss at 1,000 orders per month. At the base assumptions, the moderate-cost model needs about 1,206 orders per month to break even. This is the central financial finding of the concept, not a rounding error.", 6)

# ===========================================================================
# BREAK-EVEN
# ===========================================================================
ws = wb.create_sheet("Break-even")
sheet_title(ws, "Break-even and sensitivity", "How order volume, average order value and commission rate change the break-even point.", 6)
r = 4
r = section(ws, r, "Base case", 6)
r = header_row(ws, r, ["", "Item", "Value", "Unit", "Note", ""], [4, 42, 18, 18, 52, 2])
base = [
    ("Contribution per order", DATA["unit_economics"]["contribution"], "TZS", "AOV TZS 75,000; 8% commission; 4% returns"),
    ("Monthly ancillary revenue", DATA["break_even"]["ancillary"], "TZS", "Subscriptions + sponsored placements"),
    ("Fixed monthly opex (moderate)", DATA["assumptions"]["fixed_opex_moderate"], "TZS", "From Monthly Opex"),
    ("Break-even orders per month", DATA["break_even"]["moderate"], "orders", "(Fixed opex − ancillary) ÷ contribution per order"),
    ("Break-even orders per day", DATA["break_even"]["moderate"]/30, "orders/day", "30-day month"),
    ("Break-even GMV per month", DATA["break_even"]["moderate"]*DATA["assumptions"]["aov"], "TZS", "Orders × AOV"),
]
for label, val, unit, n in base:
    fmt = TZS if unit == "TZS" else '#,##0.0' if unit == "orders/day" else '#,##0'
    r = body_row(ws, r, ["", label, val, unit, n, ""],
                 fonts=[None, BOLD_FONT if "Break-even" in label else BODY_FONT, BOLD_FONT if "Break-even" in label else BODY_FONT, BOLD_FONT if "Break-even" in label else BODY_FONT, BOLD_FONT if "Break-even" in label else BODY_FONT, None],
                 formats=[None, None, fmt, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)

r += 1
r = section(ws, r, "Sensitivity: break-even orders per month", 6)
r = header_row(ws, r, ["AOV (TZS)", "6% commission", "8% commission", "10% commission", "Contribution/order at 8%", "Interpretation"], [16, 16, 16, 16, 22, 52])
# build a pivot from sensitivity data
by = {}
for row in DATA["break_even"]["sensitivity"]:
    by.setdefault(row["aov"], {})[row["commission_rate"]] = row
for aov in sorted(by):
    cells = [aov]
    for c in (0.06, 0.08, 0.10):
        cells.append(round(by[aov][c]["break_even_orders"]))
    cells.append(round(by[aov][0.08]["contribution_per_order"]))
    interp = "Hard at pilot volume" if by[aov][0.08]["break_even_orders"] > 1500 else ("Achievable with strong demand" if by[aov][0.08]["break_even_orders"] > 700 else "Requires high AOV or high commission")
    cells.append(interp)
    r = body_row(ws, r, cells, formats=[TZS, '#,##0', '#,##0', '#,##0', TZS, None],
                 aligns=[CENTER]*5 + [LEFT], height=28)
r += 1
r = note(ws, r, "Read across: at an AOV of TZS 50,000 and a 6% commission, the moderate-cost model needs about 3,080 orders a month to break even. At TZS 100,000 and 10%, it needs about 650. The business is therefore highly sensitive to category mix and take rate.", 6)

r += 1
r = section(ws, r, "Break-even by cost scenario", 6)
r = header_row(ws, r, ["Scenario", "Fixed opex/month", "Contribution/order", "Ancillary/month", "Break-even orders/month", "Orders/day"], None)
for name, fixed, be in (("Lean", DATA["assumptions"]["fixed_opex_lean"], DATA["break_even"]["lean"]),
                        ("Moderate", DATA["assumptions"]["fixed_opex_moderate"], DATA["break_even"]["moderate"]),
                        ("Ambitious", DATA["assumptions"]["fixed_opex_ambitious"], DATA["break_even"]["ambitious"])):
    r = body_row(ws, r, [name, fixed, DATA["unit_economics"]["contribution"], DATA["break_even"]["ancillary"], round(be), round(be/30, 1)],
                 formats=[None, TZS, TZS, TZS, '#,##0', '#,##0.0'],
                 aligns=[LEFT, CENTER, CENTER, CENTER, CENTER, CENTER], height=24)
r += 1
r = note(ws, r, "All break-even figures assume the same contribution per order. A lean launch lowers the volume hurdle sharply; it also limits the support and marketing needed to reach that volume.", 6)

r += 1
r = section(ws, r, "What-if calculator (live)", 6)
r = note(ws, r, "Pale-yellow cells are inputs. Change them and the shaded output rows recalculate. At the base inputs the calculator reproduces the static model: contribution TZS 3,730 per order and a break-even of about 1,206 orders a month. The rest of the workbook does not recalculate.", 6, height=44)
r = header_row(ws, r, ["", "Input", "Value", "Unit", "Note", ""], None)

calc_inputs = [
    ("aov", "Average order value (AOV)", DATA["assumptions"]["aov"], "TZS", TZS, "Gross basket value before returns"),
    ("comm", "Commission rate", DATA["assumptions"]["commission_rate"], "of net GMV", PCT, "Charged to the supplier on completed net sales"),
    ("pay", "Payment processing fee", DATA["assumptions"]["payment_fee_rate"], "of net GMV", PCT, "Mobile money or card gateway charge"),
    ("ret", "Return rate", DATA["assumptions"]["returns_rate"], "of GMV", PCT, "Value returned and refunded"),
    ("refund", "Refund handling rate", DATA["assumptions"]["refund_handling_rate"], "of returned value", PCT, "Inspection, repacking and reverse transport"),
    ("support", "Variable support cost", DATA["assumptions"]["support_cost_per_order"], "TZS/order", TZS, "Staff time per order"),
    ("logfee", "Logistics coordination fee", DATA["assumptions"]["logistics_fee_per_order"], "TZS/order", TZS, "Charged to the supplier"),
    ("logcost", "Logistics coordination cost", DATA["assumptions"]["logistics_cost_per_order"], "TZS/order", TZS, "Admin cost to book and monitor"),
    ("fixed", "Fixed monthly opex", DATA["assumptions"]["fixed_opex_moderate"], "TZS/month", TZS, "Moderate scenario"),
    ("anc", "Monthly ancillary revenue", DATA["break_even"]["ancillary"], "TZS/month", TZS, "Subscriptions plus sponsored placements"),
]
cell = {}
for key, label, val, unit, fmt, n in calc_inputs:
    cell[key] = f"C{r}"
    r = body_row(ws, r, ["", label, val, unit, n, ""],
                 fills=[None, INPUT_FILL, INPUT_FILL, None, None, None],
                 formats=[None, None, fmt, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=22)

r += 1
r = section(ws, r, "Calculated outputs", 6)
r = header_row(ws, r, ["", "Output", "Value", "Unit", "How it is calculated", ""], None)

net = f"({cell['aov']}*(1-{cell['ret']}))"
outputs = [
    ("Net GMV per order", f"={net}", "TZS", "AOV × (1 − return rate)", TZS),
    ("Commission per order", f"={net}*{cell['comm']}", "TZS", "Net GMV × commission rate", TZS),
    ("Payment fee per order", f"={net}*{cell['pay']}", "TZS", "Net GMV × payment fee rate", TZS),
    ("Refund handling per order", f"={cell['aov']}*{cell['ret']}*{cell['refund']}", "TZS", "AOV × return rate × handling rate", TZS),
    ("Variable support per order", f"={cell['support']}", "TZS", "Input", TZS),
    ("Logistics margin per order", f"={cell['logfee']}-{cell['logcost']}", "TZS", "Coordination fee − coordination cost", TZS),
]
for label, formula, unit, how, fmt in outputs:
    r = body_row(ws, r, ["", label, formula, unit, how, ""],
                 formats=[None, None, fmt, None, None, None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=22)

contrib_row = r
contrib_formula = (f"={net}*{cell['comm']}-{net}*{cell['pay']}-{cell['aov']}*{cell['ret']}*{cell['refund']}"
                   f"-{cell['support']}+{cell['logfee']}-{cell['logcost']}")
r = body_row(ws, r, ["", "Contribution per order", contrib_formula, "TZS", "Commission − payment − refund − support + logistics margin", ""],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, TZS, None, None, None],
             aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)

be_row = r
r = body_row(ws, r, ["", "Break-even orders per month", f'=IF(C{contrib_row}<=0,"n/a",MAX(0,({cell["fixed"]}-{cell["anc"]})/C{contrib_row}))', "orders", "(Fixed opex − ancillary) ÷ contribution", '#,##0'],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, '#,##0', None, None, None],
             aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=24)
r = body_row(ws, r, ["", "Break-even orders per day", f'=IF(ISNUMBER(C{be_row}),C{be_row}/30,"n/a")', "orders/day", "30-day month", '#,##0.0'],
             formats=[None, None, '#,##0.0', None, None, None],
             aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=22)
r = body_row(ws, r, ["", "Break-even GMV per month", f'=IF(ISNUMBER(C{be_row}),C{be_row}*{cell["aov"]},"n/a")', "TZS", "Break-even orders × AOV", TZS],
             formats=[None, None, TZS, None, None, None],
             aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=22)
r = body_row(ws, r, ["", "Net result at 1,000 orders/month", f"=1000*C{contrib_row}+{cell['anc']}-{cell['fixed']}", "TZS", "1,000 × contribution + ancillary − fixed opex", TZS],
             formats=[None, None, TZS, None, None, None],
             aligns=[CENTER, LEFT, CENTER, CENTER, LEFT, LEFT], height=22)

r += 1
r = note(ws, r, "If contribution per order is zero or negative, the calculator returns 'n/a': no volume of loss-making orders can cover fixed costs. Change one input at a time so the effect of each assumption stays visible.", 6)

# ===========================================================================
# CASH PLAN
# ===========================================================================
ws = wb.create_sheet("Cash Plan")
sheet_title(ws, "Six-month pilot cash plan", "Order ramp, contribution and cumulative cash position under each cost scenario.", 8)
r = 4
for scenario, label in (("lean", "Lean"), ("moderate", "Moderate"), ("ambitious", "Ambitious")):
    r = section(ws, r, f"{label} scenario — pilot months 1-6", 8)
    r = header_row(ws, r, ["Month", "Orders", "Contribution + ancillary", "Fixed opex", "Net", "Cumulative (one-time + pre-launch + pilot)", "", ""], None)
    cp = DATA["cash_plans"][scenario]
    for m in cp["monthly"]:
        r = body_row(ws, r, [m["month"], m["orders"], round(m["contribution_and_ancillary"]), m["fixed"], round(m["net"]), round(m["cumulative"]), "", ""],
                     formats=[None, '#,##0', TZS, TZS, TZS, TZS, None, None],
                     aligns=[CENTER, CENTER, CENTER, CENTER, CENTER, CENTER, LEFT, LEFT], height=22)
    r = body_row(ws, r, ["", "Pilot total", "", "", round(cp["pilot_net"]), "", "", ""],
                 fonts=[None, BOLD_FONT, None, None, BOLD_FONT, None, None, None],
                 fills=[None, PALE_TEAL_FILL, None, None, PALE_TEAL_FILL, None, None, None],
                 formats=[None, None, None, None, TZS, None, None, None],
                 aligns=[CENTER, CENTER, CENTER, CENTER, CENTER, CENTER, LEFT, LEFT], height=24)
    r = note(ws, r, f"Funding requirement including 6 months pre-launch, one-time costs and 10% buffer: TZS {cp['funding_requirement_with_buffer']:,.0f}.", 8)
    r += 1

# ===========================================================================
# KPI TARGETS
# ===========================================================================
ws = wb.create_sheet("KPI Targets")
sheet_title(ws, "Pilot KPI targets (hypotheses to validate)", "Targets are planning hypotheses, not results. Review weekly; revise after the first eight weeks.", 6)
r = 4
r = section(ws, r, "Pilot scorecard", 6)
r = header_row(ws, r, ["#", "Metric", "Definition", "Target", "Data source", "Frequency / owner"], [4, 30, 44, 34, 26, 24])
owners = ["Supplier success", "Catalogue", "Marketing", "Marketing", "Operations", "Finance", "Operations", "Operations", "Operations", "Marketing", "Growth", "Finance", "Support", "Supplier success", "CTO"]
for i, (name, definition, target, source, freq) in enumerate(DATA["kpis"], 1):
    r = body_row(ws, r, [f"K{i:02d}", name, definition, target, source, freq + " / " + owners[i-1]],
                 aligns=[CENTER, LEFT, LEFT, LEFT, LEFT, LEFT], height=32)
r += 1
r = note(ws, r, "Stop/revise triggers: fewer than 300 completed orders in month 3; return rate above 8%; on-time delivery below 80%; contribution margin below 2%; or a data-protection incident. These triggers should prompt a review, not automatic closure.", 6)

# ===========================================================================
# RISK REGISTER
# ===========================================================================
ws = wb.create_sheet("Risk Register")
sheet_title(ws, "Risk register", "Likelihood and impact scored 1 (low) to 5 (high). Review monthly and after each phase.", 9)
r = 4
r = section(ws, r, "Risk register", 9)
r = header_row(ws, r, ["ID", "Risk", "Category", "Likelihood (1-5)", "Impact (1-5)", "Score", "Rating", "Mitigation", "Owner"],
               [6, 44, 18, 12, 12, 8, 10, 60, 14])
for rid, risk, cat, lik, imp, mit, owner in DATA["risks"]:
    score = lik * imp
    rating = "Critical" if score >= 20 else ("High" if score >= 12 else ("Medium" if score >= 6 else "Low"))
    r = body_row(ws, r, [rid, risk, cat, lik, imp, score, rating, mit, owner],
                 formats=[None, None, None, '0', '0', '0', None, None, None],
                 aligns=[CENTER, LEFT, LEFT, CENTER, CENTER, CENTER, CENTER, LEFT, CENTER], height=44)
last_risk_row = r - 1
r += 1
r = note(ws, r, "Score = likelihood × impact. Critical (20-25) requires a board decision before launch. High (12-19) requires an owner, a mitigation plan and a review date.", 9)

# conditional formatting on score
score_range = f"F5:F{last_risk_row}"
ws.conditional_formatting.add(score_range, ColorScaleRule(start_type="num", start_value=1, start_color="C6EFCE",
                                                           mid_type="num", mid_value=12, mid_color="FFEB9C",
                                                           end_type="num", end_value=25, end_color="F8CBAD"))
dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=False,
                    showErrorMessage=True, errorTitle="Score 1-5", error="Enter a whole number from 1 to 5.")
ws.add_data_validation(dv)
dv.add(f"D5:E{last_risk_row}")

# ===========================================================================
# DECISION MATRIX
# ===========================================================================
ws = wb.create_sheet("Decision Matrix")
sheet_title(ws, "Group decision matrix", "Each founder scores independently, then the group reconciles. Weights should be agreed before scoring.", 6)
r = 4
r = section(ws, r, "Scoring guide", 6)
guide = [
    ("1", "Strongly negative", "The evidence argues against proceeding on this criterion."),
    ("2", "Weak", "Material concerns outweigh the benefits."),
    ("3", "Neutral / unknown", "Insufficient evidence or balanced trade-offs."),
    ("4", "Positive", "Credible benefits with manageable concerns."),
    ("5", "Strongly positive", "Compelling, evidence-backed advantage."),
]
r = header_row(ws, r, ["Score", "Meaning", "Description", "", "", ""], None)
for s, m, d in guide:
    for col, val, al in ((1, s, CENTER), (2, m, LEFT), (3, d, LEFT)):
        c = ws.cell(row=r, column=col, value=val)
        c.font = BODY_FONT
        c.alignment = al
        c.border = BORDER
    for col in range(1, 7):
        ws.cell(row=r, column=col).border = BORDER
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=6)
    ws.row_dimensions[r].height = 22
    r += 1
r += 1

r = section(ws, r, "Weighted criteria", 6)
r = header_row(ws, r, ["#", "Criterion", "Weight", "Score (1-5)", "Weighted score", "What good looks like"], [4, 30, 10, 12, 14, 60])
first_matrix_row = r
for i, (crit, weight, what) in enumerate(DATA["decision_criteria"], 1):
    r = body_row(ws, r, [f"C{i}", crit, weight, None, None, what],
                 formats=[None, None, '0%', '0', '0.00', None],
                 aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=38)
    ws.cell(row=r-1, column=4).fill = INPUT_FILL
    ws.cell(row=r-1, column=5, value=f'=IF(D{r-1}="","",C{r-1}*D{r-1})').number_format = '0.00'
    ws.cell(row=r-1, column=5).border = BORDER
    ws.cell(row=r-1, column=5).alignment = CENTER
last_matrix_row = r - 1
r = body_row(ws, r, ["", "Total", sum(w for _, w, _ in DATA["decision_criteria"]), "", f'=IF(COUNT(E{first_matrix_row}:E{last_matrix_row})=0,"",SUM(E{first_matrix_row}:E{last_matrix_row}))', "Maximum possible score = 5.00"],
             fonts=[None, BOLD_FONT, BOLD_FONT, BOLD_FONT, BOLD_FONT, None],
             fills=[None, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, PALE_TEAL_FILL, None],
             formats=[None, None, '0%', None, '0.00', None],
             aligns=[CENTER, LEFT, CENTER, CENTER, CENTER, LEFT], height=26)
r += 1

score_dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
score_dv.promptTitle = "Score 1-5"
score_dv.prompt = "Enter a whole number from 1 (strongly negative) to 5 (strongly positive)."
score_dv.errorTitle = "Invalid score"
score_dv.error = "Use a whole number from 1 to 5, or leave the cell blank."
ws.add_data_validation(score_dv)
score_dv.add(f"D{first_matrix_row}:D{last_matrix_row}")

r = section(ws, r, "Decision thresholds", 6)
thresholds = [
    ("4.00 - 5.00", "Proceed to formal research and partner discussions; prepare a budget."),
    ("3.00 - 3.99", "Proceed only to low-cost validation; resolve the weakest criterion first."),
    ("2.00 - 2.99", "Pause. Redesign the model or narrow the scope before spending."),
    ("Below 2.00", "Do not proceed. Record the reasons and revisit only if conditions change."),
]
r = header_row(ws, r, ["Weighted score", "Recommended decision", "", "", "", ""], None)
for s, d in thresholds:
    c = ws.cell(row=r, column=1, value=s)
    c.font = BODY_FONT
    c.alignment = CENTER
    c.border = BORDER
    c = ws.cell(row=r, column=2, value=d)
    c.font = BODY_FONT
    c.alignment = LEFT
    c.border = BORDER
    for col in range(1, 7):
        ws.cell(row=r, column=col).border = BORDER
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    ws.row_dimensions[r].height = 22
    r += 1
r += 1
r = note(ws, r, "Do not average away disagreement. If any founder scores a criterion 1 or 2, discuss the reason before calculating the total. Record dissent in the minutes.", 6)

# ===========================================================================
# ROADMAP
# ===========================================================================
ws = wb.create_sheet("Roadmap")
sheet_title(ws, "Phased implementation roadmap", "Seven phases. The sequence does not depend on an agreement with Usiri.", 6)
r = 4
r = section(ws, r, "Phases, deliverables and decision gates", 6)
r = header_row(ws, r, ["Phase", "Duration", "Key deliverables", "Indicative budget (TZS)", "Dependencies", "Go / stop criteria"], [28, 14, 46, 18, 26, 46])
for phase, duration, deliverables, budget, deps, gate in DATA["roadmap"]:
    r = body_row(ws, r, [phase, duration, deliverables, budget, deps, gate],
                 aligns=[LEFT, CENTER, LEFT, CENTER, LEFT, LEFT], height=50)
r += 1
r = note(ws, r, "Phases 1-3 are cheap and reversible. Do not commit to Phase 5 spending until Phase 2 evidence and Phase 3 carrier interest are documented. A rejection by Usiri should trigger the fallback track, not the end of the project.", 6)

# ===========================================================================
# SOURCES
# ===========================================================================
ws = wb.create_sheet("Sources")
sheet_title(ws, "Source register", "Sources actually reviewed for this concept pack. Self-reported company claims are labelled.", 6)
r = 4
r = section(ws, r, "Sources and what they support", 6)
r = header_row(ws, r, ["Publisher", "Document", "URL", "Accessed", "Used for", "Limitations"], [24, 32, 52, 14, 44, 44])
for pub, doc, url, accessed, used, limits in DATA["sources"]:
    r = body_row(ws, r, [pub, doc, url, accessed, used, limits],
                 fonts=[BODY_FONT, BODY_FONT, LINK_FONT, BODY_FONT, BODY_FONT, BODY_FONT],
                 aligns=[LEFT, LEFT, LEFT, CENTER, LEFT, LEFT], height=40)
    cell = ws.cell(row=r-1, column=3)
    cell.hyperlink = url
r += 1
r = note(ws, r, "Where a figure differs between sources, the pack presents a range or states the discrepancy. No market share, customer number or financial result has been invented.", 6)

# ---------------------------------------------------------------------------
# Page setup and properties
# ---------------------------------------------------------------------------
for sheet in wb.worksheets:
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.freeze_panes = "A4"
    sheet.auto_filter.ref = None

wb.properties.title = "Proposed multi-vendor marketplace — budget and decision workbook"
wb.properties.subject = "Concept-stage feasibility analysis"
wb.properties.creator = "Founding group"
wb.properties.description = "Illustrative planning model; not an approved project or partnership."
wb.calculation.fullCalcOnLoad = True

wb.save(OUT)
print(f"Wrote {OUT}")
