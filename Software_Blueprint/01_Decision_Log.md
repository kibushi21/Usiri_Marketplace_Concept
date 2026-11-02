# Decision Log — Usiri Marketplace software blueprint

**Project:** Usiri Marketplace (working name)  
**Document ID:** UM-DEC-001  
**Version:** 0.2  
**Date opened:** 30 October 2026  
**Last updated:** 30 October 2026  
**Owner:** Founding group  
**Rule:** Decisions are recorded, dated and versioned. A decision is never silently edited; a later change is a new entry that references the original.

## Status definitions

| Status | Meaning |
|---|---|
| **Awaiting founder input** | The decision blocks the BRD or SRS and must be answered at the next review. |
| **Proposed** | A recommendation is on the table and is being designed against, but is not yet formally accepted. |
| **Decided** | Accepted by the authorised founders; the date and approvers are recorded. |
| **Superseded** | Replaced by a later decision; the replacement is referenced. |
| **Deferred** | Deliberately postponed; the trigger for reopening is recorded. |

## Decisions

The **Recommended default** column records the proposal put to the founders at the time of asking. It is retained for audit. The decision actually taken is recorded in the **Status**, **Date** and **Supersedes** fields and, in full, in [§ Recorded outcomes — 30 October 2026](#recorded-outcomes--30-october-2026).

| ID | Decision | Recommended default | Alternatives considered | Consequence of the default | Blocking? | Owner | Status | Date | Supersedes |
|---|---|---|---|---|---|---|---|---|---|
| D-01 | Launch scope: what the first release sells, where, and to how many suppliers | Dar es Salaam mainland; home, kitchen and small electrical goods in TZS 30,000–250,000; 25–40 verified suppliers | Broader general merchandise; electronics-first; multi-city | Focused catalogue, manageable returns and coherent launch message | Yes | Founders | **Decided — general merchandise** (bounded six-department scope; see outcome) | 30 Oct 2026 | — |
| D-02 | Fulfilment model: who holds stock and who moves parcels | Suppliers hold stock; platform coordinates licensed carriers; no warehouse or fleet | Marketplace hub; supplier self-delivery; dropship | Asset-light operations; platform owns the customer promise but not the assets | Yes | Founders | **Decided — as recommended** | 30 Oct 2026 | — |
| D-03 | Payment and settlement: how money is collected and suppliers are paid | Licensed PSP collects; platform settles after delivery plus return window, with holds and maker-checker | Split settlement at capture; cash on delivery; hybrid | Clear separation of customer money, revenue and supplier payable; slower supplier cash | Yes | Founders and finance lead | **Decided — as recommended** | 30 Oct 2026 | — |
| D-04 | Build route, team and timeline | Custom modular monolith (Next.js, TypeScript, FastAPI, PostgreSQL); technical lead plus one developer; 8–12 weeks | Hosted marketplace first; hybrid; 16–20 week part-time custom build | Control over order, settlement and carrier logic; higher build responsibility | Yes | Founders and CTO | **Decided — custom monolith; 8–12 weeks accepted as a stretch target** | 30 Oct 2026 | — |
| D-05 | Order structure | Parent order plus supplier orders plus shipments plus order items | One order per supplier; single flat order | Correct partial fulfilment, refunds and settlement | No, but needed before DB design | CTO | Proposed | 30 Oct 2026 | — |
| D-06 | Order state model | Separate payment, supplier order, shipment, return and dispute dimensions; derived customer summary | Single status enum; status per supplier only | Avoids contradictory states; requires projection logic | No, but needed before API design | CTO | Proposed | 30 Oct 2026 | — |
| D-07 | Commission and fee rules | Configurable, effective-dated 8% hypothesis; final rate after supplier research | Fixed rate in code; tiered commission at launch | Prevents historical recalculation; supports negotiation | No | Founders and finance | Proposed pending research | 30 Oct 2026 | — |
| D-08 | Return window and payout hold | 7-day return window from delivery; supplier payout after delivery plus hold; dispute freeze | Immediate payout; 14-day window; payout on dispatch | Protects refund capacity; suppliers wait longer for cash | No, but affects cash plan | Founders and finance | Proposed pending legal and supplier input | 30 Oct 2026 | — |
| D-09 | Logistics operating mode | Manual Mode A at pilot; provider adapter contract designed now; API only with a capable carrier | API-first; single-carrier dependency; self-delivery | No dependency on a Usiri API; operational learning is captured in structured data | No | Operations lead | Proposed | 30 Oct 2026 | — |
| D-10 | Brand and franchise configuration | Build configurable brand, territory, fee and approval capability; keep inactive until written licence | Build only after licence; hard-code Usiri branding | No implied affiliation; avoids rework if a licence is signed | No | Founders and counsel | Confirmed direction | 30 Oct 2026 | — |
| D-11 | Hosting and data location | Managed cloud; region chosen after counsel advice; no vendor lock-in in the domain model | Local hosting only; single vendor platform | Compliance and cost decision deferred with a clear owner | No, but needed before architecture sign-off | CTO and counsel | Open | — | — |
| D-12 | Language and support hours | Swahili default, English available; support 09:00–18:00 Monday–Saturday at pilot | English only; 24/7 support | Content and staffing plan; SLA text | No | Founders and operations | Proposed | 30 Oct 2026 | — |
| D-13 | Exact six launch departments and their category tree | Homeware/storage/kitchenware; small kitchen and home appliances; fashion/footwear; beauty/personal care; baby/maternity; home/kitchen bundles | Fewer, deeper departments; add electronics later | Sets catalogue, carrier handling and returns rules | Yes, before BRD sign-off | Founders and product | Open — raised by D-01 | 30 Oct 2026 | — |
| D-14 | Minimum delivered basket or small-order fee | TZS 30,000 minimum delivered basket, or a disclosed small-order fee below it | No minimum; flat delivery fee; supplier-funded delivery | Protects unit economics at a lower average order value | Yes, before pricing design | Founders and finance | Open — raised by D-01 | 30 Oct 2026 | — |
| D-15 | Category commission schedule | One 8% headline rate, with a category table and effective dating | Uniform rate; category rates; supplier-negotiated rates | Revenue model and supplier contracts | Yes, before SRS pricing rules | Founders and finance | Open — raised by D-01 | 30 Oct 2026 | — |
| D-16 | Beauty authenticity and expiry evidence | Batch/expiry capture, supplier declaration, sample audit, no medicinal claims | Declaration only; brand authorisation letters; category exclusion | Counterfeit and expired-goods exposure | Yes, before beauty category go-live | Founders and category lead | Open — raised by D-01 | 30 Oct 2026 | — |
| D-17 | Baby and child safety declaration | Mandatory safety declaration plus recall watch and immediate suspension power | Standard listing only; third-party certification | Child-safety liability and reputational risk | Yes, before baby category go-live | Founders and category lead | Open — raised by D-01 | 30 Oct 2026 | — |
| D-18 | Fashion fit and return policy | 7-day return for unworn items with tags; size guides mandatory; no return on intimate apparel | No fashion returns; exchange only; extended window | Return rate and supplier cost in fashion | Yes, before fashion category go-live | Founders and operations | Open — raised by D-01 | 30 Oct 2026 | — |
| D-19 | Launch supplier cohort and category mix | 40 verified suppliers weighted to homeware and fashion; 800–1,200 SKUs | 25 suppliers; 60 suppliers; category-even split | Supply density and catalogue credibility | Yes, before launch readiness gate | Founders and supplier lead | Open — raised by D-01 | 30 Oct 2026 | — |
| D-20 | Timeline fallback if the 8–12 week target slips | Hold the date by cutting departments at the week-8 gate; do not extend silently | Extend to 12–16 weeks; reduce feature scope; add a developer | Delivery credibility versus scope | Yes, at the week-8 gate | Founders and CTO | Open — raised by D-01 | 30 Oct 2026 | — |

## Recorded outcomes — 30 October 2026

Four blocking decisions were put to the founding group and answered on 30 October 2026. They are recorded here in full. The scope consequences are elaborated in **UM-AMD-001, Decision Outcome and Scope Amendment**.

### D-01 — Launch scope
- **Date:** 30 October 2026
- **Decided by:** Founding group
- **Decision:** Launch with **general merchandise**, not the focused home-and-kitchen pilot. The scope is bounded to six departments in Dar es Salaam: homeware, storage and kitchenware; small kitchen and home appliances; fashion and footwear; beauty and personal care; baby and maternity; home and kitchen bundles. Target 40 verified suppliers and 800–1,200 SKUs at launch, rising to 60 suppliers by month six.
- **Reason:** Founders judged that a broader assortment is needed to test demand and to present a credible marketplace to customers and suppliers.
- **Alternatives rejected:** The focused pilot recommended in UM-DISC-001 §3. Also rejected at this stage: electronics-first and multi-city launch.
- **Evidence relied on:** Concept document market sizing and competitor review; no primary supplier or customer research yet. This is a founder judgement, not an evidenced demand finding.
- **Consequences accepted:** Variants become launch-critical rather than later-phase. Category-specific attributes, size guides, authenticity controls and baby-safety controls enter MVP. Moderation load, photography cost and return complexity rise. Average order value is likely to fall below the single-category case; the unit economics must be retested.
- **Dissent recorded:** The analysis in UM-DISC-001 recommended a narrower pilot for faster learning and lower operational risk. That recommendation is superseded, and the risk is carried in RSK-16 and RSK-17.
- **Review trigger:** Week-8 scope gate, or earlier if supplier recruitment cannot reach 30 verified suppliers in the six departments.
- **Supersedes / superseded by:** Supersedes the scope recommendation in UM-DISC-001 §3 and §12. Creates D-13 to D-20. Not superseded.

### D-02 — Fulfilment model
- **Date:** 30 October 2026
- **Decided by:** Founding group
- **Decision:** **Suppliers hold stock; the platform coordinates licensed carriers.** No platform warehouse, no platform fleet, no platform-employed riders at launch.
- **Reason:** Asset-light operations, consistent with the concept and with available capital.
- **Alternatives rejected:** Marketplace hub; supplier self-delivery; dropship-only.
- **Consequences accepted:** The platform owns the delivery promise but not the assets, so carrier performance must be measured and rated. Supplier dispatch discipline becomes an operational dependency. Multi-supplier baskets create multiple shipments and split delivery fees.
- **Review trigger:** If more than 20% of launch orders need manual carrier intervention, revisit.
- **Supersedes / superseded by:** None.

### D-03 — Payment and settlement
- **Date:** 30 October 2026
- **Decided by:** Founding group
- **Decision:** A **licensed payment service provider collects customer payment**; the platform **pays suppliers after delivery plus the return window**, with holds, maker-checker approval and a reconciliation report. The platform does not hold customer funds as an informal escrow.
- **Reason:** Keeps the platform outside unlicensed deposit-taking, while protecting refund capacity.
- **Alternatives rejected:** Split settlement at capture; cash on delivery; hybrid.
- **Evidence relied on:** Bank of Tanzania licensing position summarised in UM-DISC-001 REG-04. Counsel must confirm the settlement structure before go-live.
- **Consequences accepted:** Suppliers wait for cash, which affects recruitment. A supplier payable ledger, payout holds and a reconciliation process are MVP, not later-phase.
- **Review trigger:** Before the first live payout, and on any change of PSP.
- **Supersedes / superseded by:** None.

### D-04 — Build route, team and timeline
- **Date:** 30 October 2026
- **Decided by:** Founding group
- **Decision:** **Custom modular monolith** — Next.js and TypeScript front end, FastAPI back end, PostgreSQL, Redis, object storage — built by a technical lead plus one developer, targeting **8–12 weeks**.
- **Reason:** The order, settlement and carrier logic is the product; a hosted template cannot express it.
- **Alternatives rejected:** Hosted marketplace first; hybrid; 16–20 week part-time custom build.
- **Consequences accepted:** The team carries build and operational responsibility. 8–12 weeks is accepted as a **stretch target**, not a commitment; the realistic range with two people is 12–16 weeks once payment, carrier and category work is counted. D-20 records the fallback.
- **Review trigger:** Week-8 scope gate; any integration or hiring slip.
- **Supersedes / superseded by:** None.

## Decision record template

When a decision is made, append a record in this format:

```
### D-XX — Short title
- Date:
- Decided by:
- Decision:
- Reason:
- Alternatives rejected and why:
- Evidence relied on:
- Consequences accepted:
- Dissent recorded:
- Review trigger:
- Supersedes / superseded by:
```

## Change control

1. Only the founders, or a delegate named in writing, may mark a blocking decision as **Decided**.
2. The product owner maintains this log; the CTO must be consulted on D-05, D-06, D-09 and D-11.
3. A change to a decided item requires a new row or a new version, not an edit to history.
4. Every stage gate reviews the log for decisions that are still open past their needed-by date.
5. A scope change arising from a decision is issued as a separate amendment document and cross-referenced here; the discovery report is not rewritten retrospectively.

## Version history

| Version | Date | Change | Author |
|---|---|---|---|
| 0.1 | 30 Oct 2026 | Log opened; D-01 to D-12 proposed | Project initiator |
| 0.2 | 30 Oct 2026 | D-01 to D-04 recorded as decided; outcomes written up; D-13 to D-20 opened by the D-01 scope amendment | Project initiator |
