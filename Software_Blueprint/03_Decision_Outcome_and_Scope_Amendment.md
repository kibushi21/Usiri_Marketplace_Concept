# 0. Document control

| Field | Value |
|---|---|
| Document | Decision Outcome and Scope Amendment |
| Project | Usiri Marketplace (working name) |
| Document ID | UM-AMD-001 |
| Version | 1.0 |
| Status | **Decisions recorded. Scope amended. No implementation authorized.** |
| Date | 30 October 2026 |
| Prepared for | The founding group |
| Related documents | UM-DISC-001 Requirements Discovery Report v0.2; UM-DEC-001 Decision Log v0.2 |
| Effect | Amends the launch scope in the discovery report; the rest of the discovery baseline remains in force |

> **What this document does.** It records the four blocking decisions taken on 30 October 2026 and converts the choice of **general merchandise** into a bounded, designable launch scope. It also states the consequences for the data model, supplier onboarding, returns, compliance, budget and timeline. It does not authorize build work.

---

# 1. Decisions recorded

| ID | Decision | Outcome | Effect on the baseline |
|---|---|---|---|
| D-01 | Launch scope | **General merchandise** | Replaces the focused home-and-kitchen recommendation. The category boundary, supplier count and price bands are defined in Section 3. |
| D-02 | Fulfilment | **Supplier-held stock; platform-coordinated licensed carriers; no warehouse or fleet** | Confirms the asset-light model in the concept and discovery report. |
| D-03 | Payment and settlement | **Licensed PSP collects; platform settles suppliers after delivery plus the return window, with holds and maker-checker** | Confirms the proposed payment boundary. Legal and PSP confirmation remain open. |
| D-04 | Build route | **Custom modular monolith; Next.js, TypeScript, FastAPI, PostgreSQL; 8–12 week target** | Confirms the proposed architecture. The broader catalogue adds variant and moderation scope; the timeline tension is addressed in Section 12. |

The decision log records the date, the chosen option and the consequences. The original recommendation for D-01 was a focused Dar es Salaam pilot in home, kitchen and small electrical goods. The founders chose a broader assortment. This amendment does not pretend the original recommendation was wrong; it manages the consequences of the choice.

---

# 2. Why general merchandise changes more than the catalogue

A marketplace that sells only home and kitchen goods can use a simple product model: one product, a few sizes, a price, a stock count and a warranty. General merchandise adds departments with different data, different returns behaviour and different risks:

- **Fashion and footwear** need size, colour and fit variants, size guides, and a return process built for fit failure. Return rates are structurally higher than for homeware.
- **Beauty and personal care** need authenticity controls, batch or expiry data, ingredient and claims review, and hygiene rules for opened products.
- **Baby and maternity** need safety declarations, age grading, recall awareness and stricter supplier verification.
- **Small appliances** still need warranty handling and functional testing.
- **Homeware and storage** remain the simplest category and the anchor for basket value.

The system therefore needs **variants at launch**, not later; **category-specific attributes and moderation checklists**; **category-specific return rules**; and **a catalogue operations capability** that a small team can actually run. These are not cosmetic additions. They change the database design, the supplier onboarding flow, the checkout validation and the support script.

---

# 3. D-01: The bounded general merchandise scope

## 3.1 Geography and supplier base

| Dimension | Decision | Note |
|---|---|---|
| City | Dar es Salaam mainland | Unchanged from the concept; multi-city remains deferred |
| Language | Swahili default, English available | Unchanged |
| Supplier count at launch | **40 verified suppliers** | Enough to cover six departments without overwhelming onboarding; 25–40 was the old range |
| Supplier count by month 6 | 60 | Consistent with the concept's growth path |
| Active SKUs at launch | **800–1,200** | At 20–30 active SKUs per supplier; shallow depth is deliberate |
| Supplier profile | Registered business or verifiable sole trader with a fixed shop, TIN, payout account in the business name, and ability to pack to standard | Unchanged, with category-specific additions |

Forty suppliers across six departments is a minimum for credible choice. It is not a licence to list everything a supplier stocks. The catalogue should carry the supplier's best-selling, photographable, returnable range, not its entire inventory.

## 3.2 Launch departments and boundary

| Department | Include at launch? | Conditions and category notes |
|---|---|---|
| Homeware, storage and kitchenware | **Yes** | Lowest risk; anchor for basket value; accurate dimensions and material descriptions |
| Small kitchen and home appliances | **Yes** | Functional guarantee; plug and voltage information; warranty terms; exclude high-value or installed appliances |
| Fashion and footwear | **Yes, bounded** | Size and colour variants; size guide; fit-based return reasons; no high-value designer or counterfeit-prone brands without brand authorisation |
| Beauty and personal care | **Yes, bounded** | Authenticity evidence; batch or expiry where applicable; no medical claims; opened-item hygiene exclusions; restricted products blocked |
| Baby and maternity | **Yes, bounded** | Safety declarations; age grading; no recalled or restricted items; stricter supplier verification; feeding and hygiene exclusions |
| Consumer electronics and phones | **No at launch** | High value, counterfeit, theft, warranty and price-transparency risk. Revisit after operations are stable and a warranty process exists |
| Groceries and fresh food | **No** | Perishability, cold chain and low basket value do not fit the model |
| Furniture | **No** | Bulky, assembly and delivery complexity |
| Building materials | **No** | Weight, delivery and B2B sales cycle |
| Restricted and prohibited goods | **Never** | Weapons, medicines, hazardous chemicals, stolen goods, counterfeit goods, recalled products |

**Interpretation.** "General merchandise" in this project means a **multi-department consumer assortment of six bounded departments**, not an unlimited catalogue. The boundary is a condition of a safe launch, not a retreat from the founders' choice.

## 3.3 Price bands and basket economics

The old single band of TZS 30,000–250,000 no longer fits a multi-department assortment. The following bands are proposed for testing:

| Department | Proposed launch band (TZS) | Reason |
|---|---|---|
| Homeware and storage | 20,000–200,000 | Basket anchor; bulky items need volumetric pricing |
| Small appliances | 40,000–250,000 | Warranty and functional testing justify higher value |
| Fashion and footwear | 25,000–150,000 | Lower-priced items need a basket threshold to cover delivery |
| Beauty and personal care | 15,000–100,000 | Small parcels; authenticity risk rises with branded goods |
| Baby and maternity | 20,000–150,000 | Safety and quality checks; some items are low value |
| Home and kitchen bundles | 50,000–250,000 | Encourages basket size and one delivery |

**Critical economics consequence.** The concept's unit economics assume an average order value of TZS 75,000. A broad assortment with fashion and beauty will pull the average down. The platform should test a **minimum delivered order value** (for example TZS 30,000) or a small-order fee, and should not promise free delivery on low-value baskets. The exact rule is **[Open]** and must be tested with customers before the checkout is frozen.

## 3.4 What "variants at launch" means

| Requirement | Consequence |
|---|---|
| Product has options such as size, colour, scent, pack size or model | The catalogue needs option types and option values, not just a product row |
| Each combination has its own SKU, price, stock and barcode where available | Inventory and order lines attach to the variant, not the parent product |
| Images may differ by colour | Media can attach to a variant as well as to the product |
| Size guides are category-specific | A content and attribute model is needed for fashion and baby |
| Price and stock can differ by variant | Cart validation and checkout must operate at variant level |
| Search and filters use category attributes | Attribute definitions are data, not hard-coded columns for one category |

This is the single largest technical consequence of D-01. A product model that assumes one SKU per product will fail in fashion and beauty within the first week.

## 3.5 Catalogue operations

General merchandise multiplies moderation work. The platform needs:

- **Category-specific checklists** for listing approval, not one generic checklist.
- **Attribute templates** per department, so suppliers cannot omit size, material, age grading or expiry.
- **Photo standards** by category, including scale and colour accuracy for fashion and authenticity cues for beauty.
- **A moderation queue with reasons and resubmission**, so suppliers can fix rather than guess.
- **Periodic audits** of live listings, not only first approval.
- **A prohibited-item list** maintained as configuration and reviewed when regulations or recalls change.

A team of one operations lead and one part-time moderator cannot approve 1,000 listings in a week. The launch plan must phase supplier onboarding and listing approval, or the catalogue will be either late or unchecked.

---

# 4. D-02: Fulfilment confirmed

The founders confirmed supplier-held stock and platform-coordinated carriers, with no warehouse and no fleet.

**What this means for the build:**

- The logistics module remains provider-agnostic and supports manual coordination first.
- The platform records the shipment, carrier, waybill, weight, cost, status events and proof of delivery.
- The supplier packs and hands over; the platform or carrier confirms delivery.
- A second carrier is qualified before pilot, regardless of any Usiri relationship.
- The delivery promise must accommodate category differences: a fashion parcel and a small appliance may have different handling and insurance needs.

**What remains open:** carrier selection, rates, volumetric rules, liability, insurance and whether any carrier offers an API. None of these is assumed.

---

# 5. D-03: Payment and settlement confirmed

The founders confirmed that a licensed PSP collects the full order and the platform settles suppliers after delivery plus the return window, with holds and maker-checker approval.

**What this means for the build:**

- One customer payment per checkout, allocated across supplier orders and items in the ledger.
- Commission, coordination fee, carrier payable and supplier payable are separate ledger accounts.
- Refunds are processed against the original payment; partial refunds are allocated per line and delivery share.
- Supplier payouts are held until delivery plus the return window, and may be frozen by a dispute, negative balance or KYC issue.
- The platform does not describe itself as escrow or hold customer funds in a wallet.

**What remains open:** PSP selection, fees, settlement product, payout timing, refund API, chargeback handling and the legal characterisation of the flow. Counsel and the PSP must confirm before build.

---

# 6. D-04: Build route confirmed, with a timeline warning

The founders confirmed a custom modular monolith using Next.js, TypeScript, FastAPI and PostgreSQL, with an 8–12 week target.

**The warning is specific:** the discovery baseline assumed a focused home-and-kitchen catalogue. General merchandise adds variants, category attributes, six moderation checklists, size guides, authenticity controls and a broader returns process. These are not cosmetic; they add design, build and test work.

**Options to keep 8–12 weeks credible:**

1. **Reduce department depth, not department count.** Launch all six departments but with 40 suppliers and 800 SKUs, not 1,200. Accept a shallow catalogue at launch.
2. **Use a category template.** Build one flexible attribute and variant system, then configure six templates. Do not build six bespoke catalogue modules.
3. **Defer non-essential experience work.** No recommendations, no loyalty, no chat, no native app, no automated payouts.
4. **Protect the critical path.** Variants, multi-supplier orders, payment verification, shipment records and refunds come before merchandising polish.
5. **Set a scope-cut list at week 8.** If variants and checkout are not stable, cut departments to four for the pilot rather than extend indefinitely.

If the team is part-time, or if the PSP and carrier integrations are not available by week 2, the realistic estimate is **12–16 weeks**, not 8–12. The founders should treat 8–12 weeks as a stretch target with a written scope-cut list, not as a promise to suppliers or customers.

---

# 7. Impact on the discovery baseline

| Discovery area | What changes | Action |
|---|---|---|
| Scope (Section 3) | Six departments; 40 suppliers; 800–1,200 SKUs; category-specific price bands | Superseded by this amendment |
| Stakeholders (Section 4) | More suppliers, more category-specific moderation and support work | BRD to add category owners or moderation capacity |
| Capability map (Section 6) | Variants become must-have at launch; category attributes and size guides become must-have | SRS to promote variants and attributes to MVP |
| Order model (Section 8) | Order items attach to variants; returns are category-sensitive | Database design to model variant-level order lines |
| Business rules (Section 9) | Add rules for variants, category returns, authenticity, safety and minimum basket | See Section 9 of this amendment |
| NFRs (Section 10) | Search and filters must handle variants and attributes; moderation queue must handle volume | NFR targets unchanged; capacity assumptions revised |
| Regulatory (Section 11) | Beauty claims, baby safety, product recalls and counterfeit risk need explicit controls | Counsel and compliance review before launch |
| Evidence gaps (Section 13) | Add fashion fit, beauty authenticity, baby safety and category return evidence | See Section 10 of this amendment |
| Risks (Section 15) | Add category sprawl, counterfeit, return-rate and moderation risks | See Section 11 of this amendment |
| Decisions (Section 14) | D-01 to D-04 decided; new sub-decisions opened | See Section 13 of this amendment |

---

# 8. Revised assumptions

| ID | Old assumption | Revised assumption | Status |
|---|---|---|---|
| A-02 | Home, kitchen and small electrical goods, TZS 30,000–250,000 | Six bounded departments with category-specific bands | **Revised by D-01** |
| A-03 | 25–40 suppliers | 40 at launch, 60 by month 6 | **Revised** |
| A-04 | 900 orders in month 6 | Unchanged as a planning target, but average order value must be re-tested because of the broader mix | **To test** |
| A-05 | 8% commission, tested 6–12% | Unchanged; category-level commission may be needed later | **To test** |
| A-06 | TZS 5,000 delivery charge | Unchanged as a hypothesis; minimum basket or small-order fee to be tested | **To test** |
| A-09 | Support 09:00–18:00 Monday–Saturday | Unchanged, but ticket volume will be higher because of fashion fit and beauty questions | **To test** |
| A-14 | 8–12 week MVP | 8–12 weeks as a stretch target with a scope-cut list; 12–16 weeks realistic if integrations or team capacity slip | **Revised** |

The existing startup budget also needs re-costing. More suppliers, more photography, more moderation and a broader support script increase the pre-launch and operating cost. No revised figure is asserted here; the BRD must obtain quotations and update the workbook rather than reuse the old total.

---

# 9. Additional business rules

| ID | Rule | Rationale | Status |
|---|---|---|---|
| BR-033 | Every purchasable item resolves to a variant with its own SKU, price and stock; a product without a valid variant cannot be ordered. | Fashion, beauty and baby require size, colour or pack options | Proposed |
| BR-034 | Category attribute templates are configuration; a listing cannot be published until mandatory attributes for its category are complete. | Comparable listings and fewer returns | Proposed |
| BR-035 | Return eligibility and refund treatment are category-specific; hygiene, safety and opened-item exclusions must be published before purchase. | Fairness and consumer law | Open |
| BR-036 | Beauty and personal-care listings require authenticity evidence and, where applicable, batch or expiry data before approval. | Counterfeit and safety risk | Proposed |
| BR-037 | Baby and maternity listings require safety declarations, age grading and recall checks before approval. | Child safety | Proposed |
| BR-038 | The platform may set a minimum delivered order value or a small-order fee; the rule is displayed before checkout and tested with customers. | Protect contribution on low-value fashion and beauty baskets | Open |
| BR-039 | Category-level commission rates may be configured separately, but a rate change applies only to future orders. | Margin differences across departments | Proposed |
| BR-040 | A product recall or safety notice can suspend a listing and notify affected buyers without deleting order history. | Safety and audit | Proposed |

---

# 10. Additional evidence gaps

::: {.gaps-table}
| ID | Gap | Why it matters | Method | Impact if unresolved |
|---|---|---|---|---|
| GAP-19 | Fashion size and fit return rates in Dar es Salaam | Determines return policy, size guides and contribution | Supplier interviews, competitor policy review, pilot measurement | Return costs may erase fashion margin |
| GAP-20 | Beauty authenticity and expiry practices | Determines verification and liability controls | Supplier documents, brand-authorisation checks, sample audit | Counterfeit or expired goods create legal and trust risk |
| GAP-21 | Baby product safety and recall exposure | Determines listing requirements and insurance | Supplier declarations, safety checklist, counsel input | Child-safety incident and liability |
| GAP-22 | Category-specific carrier handling and insurance | Determines delivery cost and claims | Carrier quotes for representative parcels in each department | Underpriced delivery or uninsured loss |
| GAP-23 | Catalogue content and photography capacity across six departments | Determines launch date and moderation load | Supplier audit, sample photography, time-and-motion | Catalogue late or poor quality |
| GAP-24 | Customer response to a minimum basket or small-order fee | Determines checkout conversion and basket economics | Pricing test and interviews | Low-value orders lose money or customers abandon |
:::

---

# 11. Additional risks

::: {.risk6}
| ID | Risk | Likelihood | Impact | Score | Mitigation |
|---|---|---:|---:|---:|---|
| RSK-16 | Category sprawl makes the catalogue shallow and hard to trust | 4 | 4 | 16 | Six bounded departments; 40 suppliers; no high-value electronics; category owners |
| RSK-17 | Fashion return rates exceed the model | 4 | 4 | 16 | Size guides; fit reason codes; supplier scorecards; return reserve; test before scaling |
| RSK-18 | Counterfeit or expired beauty products damage trust | 3 | 5 | 15 | Authenticity evidence; batch checks; brand authorisation; spot audits; delisting |
| RSK-19 | Baby product safety incident | 2 | 5 | 10 | Safety declarations; recall checks; restricted list; insurance; counsel review |
| RSK-20 | Catalogue moderation becomes a bottleneck | 4 | 3 | 12 | Templates; phased onboarding; moderator capacity; resubmission workflow |
| RSK-21 | Broader assortment pushes the 8–12 week build beyond target | 4 | 4 | 16 | Scope-cut list; flexible category templates; week-8 gate; realistic 12–16 week fallback |
:::

---

# 12. Timeline and scope trade-off

The founders chose both general merchandise and an 8–12 week build. Those choices are in tension. The professional response is not to pretend the tension is absent; it is to define what must be true for the timeline to hold.

**Conditions for 8–12 weeks:**

- A dedicated technical lead and one full-time developer, with design support.
- PSP sandbox access and a selected carrier by week 2.
- A single flexible variant and attribute system, configured by category, not six bespoke builds.
- 40 suppliers, not 60, at launch; 800 SKUs, not 1,200.
- No native app, no chat, no wallet, no automated payouts, no recommendations.
- A written scope-cut list that reduces departments to four if week 8 finds variants, checkout or payments unstable.

**If any condition fails**, the plan should move to 12–16 weeks. A delayed, working marketplace is better than an on-time marketplace that cannot handle a size exchange or a partial refund.

---

# 13. Open sub-decisions before the BRD

| ID | Question | Recommended default | Needed by |
|---|---|---|---|
| D-13 | Exact six-department list | Homeware, small appliances, fashion, beauty, baby, home and kitchen bundles | BRD review |
| D-14 | Minimum delivered order value or small-order fee | Test a TZS 30,000 minimum delivered basket; no free delivery below it | Checkout design freeze |
| D-15 | Category-level commission | Start with one rate; configure category rates only if supplier economics require it | Supplier contracts |
| D-16 | Beauty authenticity evidence | Supplier invoice and brand authorisation where available; batch or expiry for perishable cosmetics | Beauty onboarding |
| D-17 | Baby safety declaration | Mandatory declaration plus restricted-product list; counsel review | Baby onboarding |
| D-18 | Fashion return policy | 7-day fit return, unworn with tags, customer pays reverse transport unless the item is faulty | Policy publication |
| D-19 | Launch cohort by department | At least 6 suppliers per department, 40 total | Supplier recruitment plan |
| D-20 | Timeline fallback | 12–16 weeks if week-2 integrations or week-8 variant stability fail | Roadmap sign-off |

These are narrower than the four blocking decisions. They can be resolved during BRD elaboration, but each needs an owner and a date.

---

# 14. Next step

The BRD will use this amended scope. It will restate the business objectives, the six-department boundary, the supplier and customer journeys, the operating model and the success measures in business language. The SRS will then convert the capability map and business rules into numbered, testable requirements, with variants, multi-supplier orders, payment verification, shipment records and category-sensitive returns treated as MVP.

No code will be written until the architecture and UX packs are reviewed and approved. No Usiri brand will be used until a written licence exists.
