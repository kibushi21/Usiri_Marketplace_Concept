# 0. Document control

| Field | Value |
|---|---|
| Document | Software Requirements Specification |
| Project | Usiri Marketplace (working name) |
| Document ID | UM-SRS-001 |
| Version | 1.0 |
| Status | **Draft for founder and technical review. No implementation is authorized.** |
| Date | 30 October 2026 |
| Prepared for | Founders, technical lead, design, security and test reviewers |
| Prepared by | Project initiator, acting as business analyst and software architect |
| Classification | Confidential — internal discussion |
| Baseline | UM-BRD-001 v1.0; UM-DISC-001 v0.2; UM-AMD-001 v1.0; UM-DEC-001 v0.2 |
| Next documents | System architecture, database design, API specification, security architecture, UX specification |

> **Status notice.** Usiri is a potential logistics and brand partner only. No API, rate card, franchise term or licence is assumed. The platform is carrier-agnostic and PSP-agnostic. No code has been written.

## 0.1 Conventions

- **Shall** marks a mandatory requirement. **Should** marks a requirement that may be deferred with a written decision. **May** marks an optional capability.
- Every requirement has a stable ID of the form `REQ-<module>-<number>`. IDs are never reused or renumbered.
- **Priority** uses MoSCoW: Must, Should, Could, Won't. **Must** requirements form the launch scope.
- **Source** links to a business need (BN), business rule (BR), capability (CAP) or decision (D).
- **Verification** states how the requirement will be proven. It is not a test script; it names the test approach.
- **TBC** marks a value that cannot be fixed until an open decision is answered. A TBC value must come from configuration, not from code.

---

# 1. Introduction

## 1.1 Purpose

This specification defines the software behaviour required to operate the marketplace described in the BRD. It is the contract between business, design, engineering and testing. It is detailed enough to estimate, build and test, and it deliberately stops short of prescribing the internal design.

## 1.2 Scope

The system comprises a customer web experience, a supplier portal, an operations console, a logistics coordination module, a payment and settlement module, a support and returns workflow, and the platform services that connect them. It runs as a modular monolith with a relational database, background workers, object storage and external integrations for payments, messaging and delivery.

## 1.3 Definitions

| Term | Meaning |
|---|---|
| Parent order | The customer's single commercial order created by one checkout |
| Supplier order | The part of a parent order fulfilled by one supplier; the unit of commission and settlement |
| Shipment | A physical parcel with a carrier, waybill and delivery evidence |
| Variant | A purchasable option combination with its own SKU, price and stock |
| Reservation | A temporary hold on stock while payment is in progress |
| Captured | Funds successfully taken by the PSP |
| Settled | Supplier payable released for payout after delivery and the return window |
| POD | Proof of delivery, with recipient evidence |
| Mode A | Manual carrier coordination |
| Mode B | Carrier integration through an adapter |
| TBC | To be confirmed by an open decision |

## 1.4 References

UM-DISC-001 Requirements Discovery Report v0.2; UM-BRD-001 v1.0; UM-AMD-001 v1.0; UM-DEC-001 v0.2; the concept document v1.0; the startup workbook.

---

# 2. Overall description

## 2.1 Product perspective

The system is a new, self-contained platform. It integrates with, but does not depend on, a specific payment provider or carrier. It replaces spreadsheets and messaging apps for the operating team; it does not replace the supplier's own shop or stock system, which remains the source of stock truth through portal updates or file upload.

## 2.2 Product functions

1. Customer identity, consent and addresses.
2. Supplier onboarding, verification and contracts.
3. Catalogue, variants, attributes, media and moderation.
4. Inventory and reservations.
5. Search, browse and product discovery.
6. Multi-supplier cart and checkout.
7. Order orchestration and partial fulfilment.
8. Payment initiation, verification, refunds and reconciliation.
9. Commission, statements, payouts and holds.
10. Logistics coordination, tracking, proof of delivery and claims.
11. Category-sensitive returns and disputes.
12. Customer support with order context.
13. Transactional and consent-aware notifications.
14. Administration, access control, configuration and audit.
15. Reporting and supplier scorecards.
16. Verified reviews, controlled promotions and configurable brand rules.

## 2.3 User classes

| Class | Frequency | Criticality | Notes |
|---|---|---|---|
| Guest | High | High | Must complete checkout without an account |
| Customer | High | High | Mobile, low bandwidth, Swahili-first |
| Supplier owner | Daily | High | May use a phone; needs simple tasks |
| Supplier staff | Daily | Medium | Packing and dispatch only |
| Support agent | Daily | High | Needs order context in one screen |
| Moderator | Daily | High | Queue-based work |
| Finance | Daily | High | Reconciliation and payouts |
| Operations lead | Daily | High | Exceptions and carrier coordination |
| Administrator | Weekly | High | Access and configuration |
| Carrier administrator | Daily | Medium | Assigned shipments only |
| Auditor or founder | Monthly | Medium | Read-only access to evidence |

## 2.4 Operating environment

Mobile web first, responsive to desktop. Supported browsers: current Chrome, Safari, Firefox and Android WebView. The customer experience must work on a mid-range Android device on a 4G connection, and degrade gracefully on slower devices. The supplier portal must be usable on a phone. The operations console is desktop-first. No native application is in scope.

## 2.5 Design and implementation constraints

- Modular monolith; a single deployable application with clear module boundaries.
- PostgreSQL as the system of record; Redis for ephemeral state such as sessions, rate limits and reservations.
- Object storage for media and documents, with signed access.
- All money as integer TZS.
- Server-side calculation of all prices, fees, commissions and refunds.
- No card data stored or transmitted through platform infrastructure beyond the PSP's hosted interface.
- All customer-facing strings externalised for Swahili and English.
- All brand, territory and franchise behaviour driven by configuration.
- Timezone Africa/Dar_es_Salaam for business dates; UTC for storage.

## 2.6 Assumptions and dependencies

The PSP provides signed callbacks, a status endpoint, refunds and a settlement or payout mechanism. A licensed carrier can carry the launch categories and provide a waybill and delivery evidence. SMS delivery is available to Tanzanian numbers. The team can obtain legal advice before launch. These are dependencies, not confirmed facts.

---

# 3. System context and actors

| Actor | Interaction | Trust boundary |
|---|---|---|
| Guest or customer | Web application over HTTPS | Untrusted input; authenticated for account actions |
| Supplier owner or staff | Supplier portal | Authenticated; scoped to one supplier |
| Carrier administrator or agent | Carrier view or manual coordination | Authenticated; scoped to assigned shipments |
| Support, moderator, finance, operations | Operations console | Authenticated with MFA; role-scoped |
| PSP | Server-to-server API and signed callbacks | External; verified signatures and IP allow-list where available |
| Carrier | Adapter or manual entry | External; contract and evidence |
| Messaging provider | Server-to-server API | External; template and consent rules |
| Object storage | Private bucket with signed URLs | Internal; least privilege |
| Auditor | Read-only console and exports | Authenticated; no mutation |

Data flows across these boundaries are described in Section 7. The most sensitive boundaries are the PSP callback, supplier access to customer delivery data, and staff access to KYC documents.

---

# 4. Functional requirements

## 4.1 Identity, accounts and consent (REQ-ACC)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-ACC-001 | The system shall let a customer register and sign in with a phone number verified by a one-time code. | Must | CAP-01 | OTP integration test for valid, expired and reused codes |
| REQ-ACC-002 | The system shall allow guest checkout with only the contact and address data needed to fulfil the order. | Must | BN-01, STK-01 | Guest order completes without an account |
| REQ-ACC-003 | The system shall offer account creation after a guest order without requiring re-entry of the order data. | Should | CAP-01 | Conversion test from guest order to account |
| REQ-ACC-004 | The system shall maintain a customer profile with name, phone, optional email and a list of addresses with a landmark field. | Must | CAP-01 | Create, edit and select address in checkout |
| REQ-ACC-005 | The system shall record consent per purpose against a versioned privacy notice, with timestamp and source. | Must | BR-024, NFR-PRIV-01 | Consent record inspection for each signup path |
| REQ-ACC-006 | The system shall expire idle sessions and invalidate sessions on sign-out and on credential change. | Must | NFR-SEC-01 | Session tests |
| REQ-ACC-007 | The system shall require multi-factor authentication for all staff and supplier owner accounts. | Must | NFR-SEC-03 | Login test for each privileged role |
| REQ-ACC-008 | The system shall store passwords, where used, with Argon2id and enforce a minimum length of 12 characters. | Must | NFR-SEC-03 | Code review and authentication test |
| REQ-ACC-009 | The system shall let a customer export their personal data in a machine-readable format. | Must | NFR-PRIV-03 | Export request produces complete file |
| REQ-ACC-010 | The system shall support account deletion or anonymisation while retaining records required for tax, dispute and audit. | Must | BR-024 | Deletion test with financial retention check |
| REQ-ACC-011 | The system shall keep marketing consent separate from transactional messaging and allow withdrawal at any time. | Must | BR-025 | Withdrawal stops marketing only |
| REQ-ACC-012 | The system shall rate-limit sign-in, OTP and password reset attempts and lock progressively. | Must | NFR-SEC-05 | Abuse test against limits |

## 4.2 Supplier onboarding and KYC (REQ-KYC)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-KYC-001 | The system shall accept a supplier application with business name, trading name, category, location, contact and owner details. | Must | CAP-02 | Application submitted and stored |
| REQ-KYC-002 | The system shall accept document uploads for business registration, TIN, owner identity, shop evidence and payout account evidence. | Must | CAP-02, REG-07 | Upload each document type with size and type checks |
| REQ-KYC-003 | The system shall move an application through defined states: submitted, under review, information requested, approved, rejected, suspended. | Must | CAP-02 | State transition test with reasons |
| REQ-KYC-004 | The system shall detect possible duplicate suppliers by TIN, phone number and payout account. | Should | CAP-02 | Duplicate application flagged |
| REQ-KYC-005 | The system shall record a site visit with date, visitor, location evidence and outcome. | Must | CAP-02 | Site visit recorded before approval |
| REQ-KYC-006 | The system shall store the supplier contract version accepted, with date and signatory. | Must | REG-08 | Contract record linked to supplier |
| REQ-KYC-007 | The system shall require a reason and an actor for every approval, rejection and suspension decision. | Must | BR-023 | Decision without reason is blocked |
| REQ-KYC-008 | The system shall verify that the payout account name matches the supplier's legal or trading name before approval. | Must | BR-029 | Mismatch blocks approval pending review |
| REQ-KYC-009 | The system shall schedule re-verification and flag overdue verifications, ownership changes and bank-account changes. | Must | CAP-02 | Overdue supplier appears in compliance queue |
| REQ-KYC-010 | The system shall let an authorised operator suspend a supplier, immediately hiding its listings and blocking new orders. | Must | BR-010 | Suspension test shows listings hidden |
| REQ-KYC-011 | The system shall let a supplier owner invite staff with limited permissions and revoke access immediately. | Must | ROL-04 | Invitation and revocation test |
| REQ-KYC-012 | The system shall notify the supplier of missing or expiring documents in the supplier's chosen language. | Should | CAP-13 | Notification triggered at threshold |
| REQ-KYC-013 | The system shall allow a rejected supplier to correct and resubmit without creating a duplicate record. | Should | CAP-02 | Resubmission test |
| REQ-KYC-014 | The system shall publish a supplier storefront with approved brand, description, policies and live listings only. | Must | BN-03 | Storefront shows approved content only |

## 4.3 Catalogue, variants and moderation (REQ-CAT)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-CAT-001 | The system shall maintain a category tree of six departments with configurable subcategories. | Must | BN-03, D-13 | Category administration test |
| REQ-CAT-002 | The system shall support category attribute templates with mandatory and optional fields, data types and allowed values. | Must | BR-034 | Listing cannot publish without mandatory attributes |
| REQ-CAT-003 | The system shall support products with one or more variants defined by option types such as size, colour, scent, pack size and model. | Must | BR-033 | Variant creation and purchase test |
| REQ-CAT-004 | The system shall require a unique SKU per variant and reject duplicates within a supplier account. | Must | BR-033 | Duplicate SKU rejected |
| REQ-CAT-005 | The system shall store price and stock at variant level and display a price range when variants differ. | Must | BR-033 | Price range and per-variant checkout |
| REQ-CAT-006 | The system shall support multiple images per product and per variant, with ordering, alt text and category-specific guidance. | Must | BN-03 | Media upload and ordering test |
| REQ-CAT-007 | The system shall route new and edited listings to a moderation queue with the applicable category checklist. | Must | CAP-03 | Listing enters correct queue |
| REQ-CAT-008 | The system shall let a moderator approve, reject or request changes with a reason code and a note. | Must | BR-010 | Decision recorded with reason |
| REQ-CAT-009 | The system shall prevent publication of a listing that is unapproved, out of stock, prohibited or missing mandatory attributes. | Must | BR-010, BR-015 | Publish attempt is blocked with explanation |
| REQ-CAT-010 | The system shall support bulk listing upload by CSV with per-row validation and an error report. | Should | CAP-03 | 200-row upload with mixed errors |
| REQ-CAT-011 | The system shall maintain a brand registry and flag listings that claim a brand without evidence where evidence is required. | Should | BR-036 | Brand claim routed to evidence check |
| REQ-CAT-012 | The system shall block prohibited items at listing time using a configurable keyword, category and brand list. | Must | BR-015 | Prohibited term blocked |
| REQ-CAT-013 | The system shall store category size guides and link them from fashion, baby and footwear listings. | Must | BN-03, D-18 | Size guide visible on product page |
| REQ-CAT-014 | The system shall support periodic audit of live listings by sampling or filter, with findings and corrective actions. | Should | CAP-03 | Audit sample created and recorded |
| REQ-CAT-015 | The system shall provide category-specific moderation checklists editable without deployment. | Must | BN-16 | Checklist change reflected in queue |
| REQ-CAT-016 | The system shall keep a version history of listing content, price and moderation decisions. | Must | BR-011 | Prior version retrievable |

## 4.4 Inventory and availability (REQ-INV)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-INV-001 | The system shall record stock per variant per supplier location. | Must | CAP-04 | Stock record created and read |
| REQ-INV-002 | The system shall reserve stock atomically when a payment intent is created and release it if payment fails or the reservation expires. | Must | BR-002 | Concurrent checkout test shows no oversell |
| REQ-INV-003 | The system shall apply a configurable reservation expiry, defaulting to 15 minutes. | Must | BR-002 | Expired reservation releases stock |
| REQ-INV-004 | The system shall prevent negative available stock through database-level constraints or equivalent guarantees. | Must | BN-05 | Concurrent reservation test |
| REQ-INV-005 | The system shall hide or mark unavailable a variant at zero available stock. | Must | BR-010 | Zero-stock variant not purchasable |
| REQ-INV-006 | The system shall alert a supplier when stock falls below a configurable threshold. | Should | CAP-04 | Threshold alert sent |
| REQ-INV-007 | The system shall let a supplier update stock by portal edit or file upload with an audit record. | Must | CAP-04 | Update and audit entry |
| REQ-INV-008 | The system shall record manual stock adjustments with actor, reason and before-and-after values. | Must | BR-023 | Adjustment history visible |
| REQ-INV-009 | The system shall not accept backorders at launch. | Must | D-02 | Order attempt beyond stock is blocked |

## 4.5 Search, browse and discovery (REQ-DIS)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-DIS-001 | The system shall provide keyword search across product title, brand, category and attributes in Swahili and English. | Must | CAP-05 | Search test in both languages |
| REQ-DIS-002 | The system shall support filters by category, price, availability, brand and category-specific attributes. | Must | CAP-05 | Filter combinations return correct sets |
| REQ-DIS-003 | The system shall support sorting by relevance, price and recency. | Must | CAP-05 | Sort order test |
| REQ-DIS-004 | The system shall provide department and category landing pages with curated ordering. | Must | CAP-05 | Landing page renders live products |
| REQ-DIS-005 | The system shall provide a product page with variant selection, price, stock, delivery estimate, return terms and supplier identity. | Must | BN-06 | Product page completeness check |
| REQ-DIS-006 | The system shall handle zero results with spelling suggestions, related categories and popular products. | Should | CAP-05 | Zero-result page shows alternatives |
| REQ-DIS-007 | The system shall show related products from the same category without promoting unrelated categories. | Could | CAP-05 | Related list relevance check |
| REQ-DIS-008 | The system shall present all customer-facing discovery content in the selected language. | Must | NFR-I18N-01 | Pseudo-localisation test |
| REQ-DIS-009 | The system shall record search terms and zero-result queries for merchandising review. | Should | CAP-15 | Search report available |
| REQ-DIS-010 | The system shall indicate when a product is unavailable rather than hiding it abruptly from a shared link. | Should | BN-05 | Shared link shows unavailable state |

## 4.6 Cart and checkout (REQ-CHK)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-CHK-001 | The system shall maintain one cart that may contain items from multiple suppliers. | Must | BN-01 | Three-supplier cart |
| REQ-CHK-002 | The system shall validate price and stock server-side at cart view, checkout start and order submission. | Must | BR-003 | Tampering and stale-price tests |
| REQ-CHK-003 | The system shall collect a delivery address with recipient name, phone, street or area, landmark and optional instructions. | Must | CAP-06 | Address validation test |
| REQ-CHK-004 | The system shall quote delivery per supplier shipment and show the number of parcels before payment. | Must | BN-06 | Multi-supplier quote displayed |
| REQ-CHK-005 | The system shall display item value, delivery, discounts, any small-order fee and total in TZS before payment. | Must | BN-06, BR-038 | Total breakdown visible and correct |
| REQ-CHK-006 | The system shall enforce a configurable minimum delivered order value or small-order fee, disclosed before payment. | Must | BR-038, D-14 | Below-threshold cart shows fee or block |
| REQ-CHK-007 | The system shall require acceptance of terms, returns policy and privacy notice before order submission. | Must | REG-02, BR-024 | Consent recorded with version |
| REQ-CHK-008 | The system shall support voucher or promotion codes where a valid campaign exists. | Should | CAP-17 | Valid and invalid code tests |
| REQ-CHK-009 | The system shall submit an order idempotently so that retries and double taps do not create duplicate orders. | Must | NFR-R-01 | Double-submit test creates one order |
| REQ-CHK-010 | The system shall create stock reservations before payment initiation and release them on failure or expiry. | Must | BR-002 | Reservation lifecycle test |
| REQ-CHK-011 | The system shall allow a guest to provide only the contact details required for fulfilment and support. | Must | STK-01 | Guest checkout field audit |
| REQ-CHK-012 | The system shall show an estimated delivery window per supplier based on configured handling and transit times. | Should | BN-06 | Estimate shown and labelled as estimate |
| REQ-CHK-013 | The system shall preserve cart contents across sessions for a signed-in customer for a configurable period. | Could | CAP-06 | Cart restored after sign-in |
| REQ-CHK-014 | The system shall recover gracefully from payment failure, preserving the cart and offering retry. | Must | BN-07 | Failed payment returns to cart with items |
| REQ-CHK-015 | The system shall show the supplier name and fulfilment responsibility on each cart line. | Must | BN-01 | Supplier shown per line |

## 4.7 Orders and fulfilment orchestration (REQ-ORD)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-ORD-001 | The system shall create one parent order and one supplier order per supplier at checkout. | Must | BR-001 | Three-supplier order structure |
| REQ-ORD-002 | The system shall give the supplier a configurable acceptance window, defaulting to 12 working hours, after which the supplier order may be auto-cancelled. | Must | CAP-07 | Timeout test |
| REQ-ORD-003 | The system shall allow a supplier to accept, reject or partially accept an order with a reason. | Must | BN-09 | Partial acceptance test |
| REQ-ORD-004 | The system shall allow cancellation of a supplier order before acceptance. | Must | BR-012 | Cancellation before acceptance |
| REQ-ORD-005 | The system shall allow cancellation of individual lines after acceptance only through the return or exception process. | Must | BR-012 | Post-acceptance cancel blocked |
| REQ-ORD-006 | The system shall maintain separate payment, supplier order, shipment, return and dispute states and derive a customer-facing summary. | Must | CAP-07 | State combination tests |
| REQ-ORD-007 | The system shall record every state change with actor, timestamp, reason and previous state. | Must | BR-023 | Event history inspection |
| REQ-ORD-008 | The system shall show the customer a per-supplier progress view within the parent order. | Must | BN-01 | Customer view test |
| REQ-ORD-009 | The system shall show the supplier only its own order lines and the customer data needed to fulfil. | Must | BR-013 | Supplier data visibility test |
| REQ-ORD-010 | The system shall issue a receipt or invoice per parent order and a supplier statement per settlement period. | Must | REG-06 | Document generation test |
| REQ-ORD-011 | The system shall allow a customer to reorder previous items subject to current price and stock. | Could | CAP-07 | Reorder test with changed price |
| REQ-ORD-012 | The system shall support order search by order number, phone, supplier and tracking reference. | Must | NFR-SUP-01 | Lookup under 30 seconds |
| REQ-ORD-013 | The system shall notify the customer of acceptance, dispatch, delivery and cancellation events. | Must | CAP-13 | Notification trigger test |
| REQ-ORD-014 | The system shall calculate and display the expected supplier payout date on the supplier order. | Should | BR-007 | Payout date matches policy |

## 4.8 Payments, refunds and reconciliation (REQ-PAY)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-PAY-001 | The system shall initiate payment through the PSP for the parent order total and store the PSP reference. | Must | CAP-08 | Sandbox initiation |
| REQ-PAY-002 | The system shall verify every PSP callback signature and reject unsigned or invalid callbacks. | Must | NFR-SEC-01 | Forged callback rejected |
| REQ-PAY-003 | The system shall confirm final payment status through a server-to-server PSP query before marking an order paid. | Must | BN-07 | Callback followed by status query |
| REQ-PAY-004 | The system shall process duplicate callbacks idempotently. | Must | NFR-R-01 | Repeated callback leaves one payment |
| REQ-PAY-005 | The system shall record failed, cancelled, expired and reversed payments with a reason. | Must | BN-07 | Failure state test |
| REQ-PAY-006 | The system shall support full and partial refunds against the original payment with a reason and an approver. | Must | BR-027 | Partial refund test |
| REQ-PAY-007 | The system shall prevent refunds exceeding the captured amount less prior refunds and reversals. | Must | BR-027 | Over-refund blocked |
| REQ-PAY-008 | The system shall record chargebacks and reversals with evidence and affected order lines. | Must | RSK-13 | Chargeback record created |
| REQ-PAY-009 | The system shall post every payment, refund and fee to a double-entry ledger with unique references. | Must | BN-23 | Ledger balances to zero per transaction |
| REQ-PAY-010 | The system shall reconcile PSP settlement files to the ledger daily and queue unmatched items. | Must | BN-23 | Reconciliation run with seeded mismatch |
| REQ-PAY-011 | The system shall provide an exception queue for unmatched, duplicated or amount-mismatched transactions. | Must | BN-23 | Exception appears and can be resolved |
| REQ-PAY-012 | The system shall show the customer the payment status of each order without exposing PSP credentials or card data. | Must | BN-07 | Status view test |
| REQ-PAY-013 | The system shall not store card numbers, CVV or full track data in any platform system. | Must | NFR-PRIV-02 | Data-inventory review |
| REQ-PAY-014 | The system shall allow a customer to retry a failed payment while the reservation is valid. | Must | BN-07 | Retry within window |

## 4.9 Commission, settlement and payouts (REQ-SET)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-SET-001 | The system shall calculate commission per order line on net completed merchandise using the effective rule at order time. | Must | BR-004 | Calculation test with returns and discounts |
| REQ-SET-002 | The system shall record the commission rule version on every order line. | Must | BR-011 | Rule version visible on statement |
| REQ-SET-003 | The system shall generate a supplier statement per period with orders, commission, refunds, chargebacks, adjustments and net payable. | Must | CAP-09 | Statement reconciles to ledger |
| REQ-SET-004 | The system shall make a payable eligible only after delivery plus the return window, unless a hold applies. | Must | BR-007 | Eligibility date test |
| REQ-SET-005 | The system shall apply holds for open disputes, negative balances, KYC issues and risk flags with a written reason. | Must | BR-029 | Hold blocks payout and is visible |
| REQ-SET-006 | The system shall build payout batches and require a different approver before release. | Must | BR-028 | Same-user approval blocked |
| REQ-SET-007 | The system shall export a payout file in the format required by the payment channel. | Must | CAP-09 | Export accepted by channel in test |
| REQ-SET-008 | The system shall record manual adjustments with reason, actor and approver, and reflect them in the next statement. | Must | BR-009 | Adjustment appears in statement |
| REQ-SET-009 | The system shall carry a negative supplier balance forward and offset it against future payables. | Should | BR-029 | Negative balance offset test |
| REQ-SET-010 | The system shall apply configurable tax withholding where counsel confirms a requirement. | Should | REG-06 | Withholding applied when enabled |
| REQ-SET-011 | The system shall show the supplier the payout status and reference for each paid batch. | Must | BN-08 | Supplier view test |
| REQ-SET-012 | The system shall reconcile payout channel confirmations to the payout batch and flag failures. | Must | BN-23 | Failed payout flagged |

## 4.10 Logistics and tracking (REQ-LOG)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-LOG-001 | The system shall maintain a register of carriers with services, coverage, contact details and contract status. | Must | CAP-10 | Carrier administration test |
| REQ-LOG-002 | The system shall maintain delivery zones and rate rules by carrier, weight, dimensions and category. | Must | BN-06 | Quote test for each zone and category |
| REQ-LOG-003 | The system shall create a shipment per supplier order or parcel with items, weight, dimensions and declared value. | Must | BR-016 | Shipment record test |
| REQ-LOG-004 | The system shall record carrier, service, waybill, cost and pickup date for every shipment. | Must | BR-016 | Required fields enforced |
| REQ-LOG-005 | The system shall support a manual booking mode in which an operator records the booking and status events. | Must | BR-031 | Mode A end-to-end test |
| REQ-LOG-006 | The system shall define a carrier adapter interface so an integrated carrier can replace manual entry without changing order logic. | Must | BR-031, D-09 | Adapter contract review and stub test |
| REQ-LOG-007 | The system shall record shipment status events with source, timestamp and raw reference. | Must | BN-11 | Event timeline test |
| REQ-LOG-008 | The system shall record proof of delivery with recipient name, timestamp, method and evidence where available. | Must | BR-016 | POD required before delivery completion |
| REQ-LOG-009 | The system shall record failed delivery attempts with reason and schedule a retry per policy. | Must | BR-017 | Failed attempt and retry test |
| REQ-LOG-010 | The system shall record return-to-supplier outcomes and make the items available again only after inspection. | Must | BR-018 | Returned parcel stock test |
| REQ-LOG-011 | The system shall record carrier claims with evidence, amount, status and outcome. | Should | CAP-10 | Claim lifecycle test |
| REQ-LOG-012 | The system shall provide a customer tracking page by order and shipment without exposing internal notes. | Must | BN-11 | Tracking page test |
| REQ-LOG-013 | The system shall show an estimated delivery date derived from carrier service and handling time, labelled as an estimate. | Should | BN-06 | Estimate calculation test |
| REQ-LOG-014 | The system shall compute carrier on-time and first-attempt performance from system events. | Must | BR-030 | Scorecard calculation test |
| REQ-LOG-015 | The system shall record the customer delivery charge, carrier charge and coordination margin separately. | Must | BR-005 | Three amounts visible in finance report |
| REQ-LOG-016 | The system shall produce a pickup manifest per supplier and pickup run. | Should | CAP-10 | Manifest generation test |

## 4.11 Returns, refunds and disputes (REQ-RET)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-RET-001 | The system shall determine return eligibility from delivery date, category, item condition rules and policy version. | Must | BR-035 | Eligibility matrix test |
| REQ-RET-002 | The system shall require a return reason code and allow photo evidence. | Must | CAP-11 | Request with and without evidence |
| REQ-RET-003 | The system shall display non-returnable conditions before purchase and again at request time. | Must | BR-035 | Disclosure visible |
| REQ-RET-004 | The system shall route a request to the supplier and to support according to policy and value thresholds. | Must | CAP-11 | Routing test |
| REQ-RET-005 | The system shall support approval, rejection and partial approval with a reason. | Must | CAP-11 | Decision test |
| REQ-RET-006 | The system shall coordinate reverse pickup or drop-off and record the reverse shipment. | Must | CAP-11, CAP-10 | Reverse shipment record |
| REQ-RET-007 | The system shall require inspection before refund when the policy requires it. | Should | BR-035 | Refund blocked before inspection |
| REQ-RET-008 | The system shall calculate the refund from item value, delivery share, discounts and prior refunds. | Must | BR-006, BR-027 | Calculation test |
| REQ-RET-009 | The system shall charge the refunded amount back to the supplier's payable where the supplier is responsible. | Must | BR-004 | Supplier statement reflects chargeback |
| REQ-RET-010 | The system shall support partial return of an order line quantity where the variant is identical. | Should | CAP-11 | Partial quantity test |
| REQ-RET-011 | The system shall convert a contested return into a dispute with evidence and a decision record. | Must | CAP-11 | Dispute creation test |
| REQ-RET-012 | The system shall escalate unresolved disputes past a configurable age to the operations lead. | Must | CAP-11 | SLA escalation test |
| REQ-RET-013 | The system shall notify the customer of each return and refund decision within the published service level. | Must | BN-10 | Notification test |
| REQ-RET-014 | The system shall close the return only when the refund, replacement or rejection is complete and communicated. | Must | CAP-11 | Closure state test |

## 4.12 Customer support (REQ-CS)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-CS-001 | The system shall create a ticket from a customer contact with order, supplier order and shipment context where available. | Must | CAP-12 | Ticket creation from order |
| REQ-CS-002 | The system shall display order timeline, payment status, shipment events and prior tickets on one screen. | Must | BN-12 | Support screen completeness |
| REQ-CS-003 | The system shall assign tickets by queue, category and workload. | Should | CAP-12 | Assignment rule test |
| REQ-CS-004 | The system shall track first-response and resolution timers against the service level. | Must | BN-12 | Timer breach flagged |
| REQ-CS-005 | The system shall record internal notes that are never visible to customers or suppliers. | Must | ROL-07 | Visibility test |
| REQ-CS-006 | The system shall provide approved response templates in Swahili and English. | Should | CAP-12 | Template insert test |
| REQ-CS-007 | The system shall route refund requests above a threshold to finance approval. | Must | BR-009 | Threshold routing test |
| REQ-CS-008 | The system shall record a resolution code for every closed ticket. | Must | BN-24 | Closure requires code |
| REQ-CS-009 | The system shall collect a satisfaction rating after resolution. | Should | CAP-12 | Rating stored |
| REQ-CS-010 | The system shall search tickets by customer, order, phone and reference. | Must | NFR-SUP-01 | Search test |

## 4.13 Notifications (REQ-NOT)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-NOT-001 | The system shall send transactional messages for verification, order, payment, dispatch, delivery, return and refund events. | Must | CAP-13 | Trigger test per event |
| REQ-NOT-002 | The system shall support SMS, WhatsApp and email channels, with channel availability configurable per message type. | Must | CAP-13 | Channel fallback test |
| REQ-NOT-003 | The system shall use approved templates with parameters and render them in the recipient's language. | Must | NFR-I18N-01 | Template rendering test |
| REQ-NOT-004 | The system shall send marketing messages only where consent exists and shall honour withdrawal immediately. | Must | BR-025 | Consent enforcement test |
| REQ-NOT-005 | The system shall retry failed messages and record permanent failures for follow-up. | Must | NFR-R-03 | Failure retry test |
| REQ-NOT-006 | The system shall record delivery status for each message where the provider reports it. | Should | CAP-13 | Status callback test |
| REQ-NOT-007 | The system shall allow a customer to opt out of non-essential messages without losing order updates. | Must | BR-025 | Opt-out test |
| REQ-NOT-008 | The system shall support a safety notice broadcast to affected buyers of a recalled or suspended product. | Must | BR-040 | Recall notice test |
| REQ-NOT-009 | The system shall never include full payment credentials or sensitive KYB data in a message. | Must | NFR-PRIV-02 | Message content audit |

## 4.14 Administration, access and audit (REQ-ADM)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-ADM-001 | The system shall provide staff accounts separate from customer and supplier accounts. | Must | CAP-14 | Account type separation test |
| REQ-ADM-002 | The system shall enforce role-based permissions with deny-by-default and tenant scoping for supplier users. | Must | NFR-SEC-04 | Authorisation matrix tests |
| REQ-ADM-003 | The system shall mask personal and financial data by default and reveal it only with a permission and a reason. | Must | NFR-PRIV-02 | Masking and reveal tests |
| REQ-ADM-004 | The system shall maintain configuration for fees, commission, zones, policies, checklists, templates and brand rules with effective dates. | Must | BR-022 | Configuration change without deployment |
| REQ-ADM-005 | The system shall keep an append-only audit log of authentication, role, refund, payout, price, listing and supplier-status events. | Must | BR-023 | Audit coverage test |
| REQ-ADM-006 | The system shall support time-bound break-glass access with a reason, alerting and post-hoc review. | Should | BR-026 | Break-glass grants and expires |
| REQ-ADM-007 | The system shall support controlled data export for operations and finance with permission and logging. | Must | CAP-14 | Export permission test |
| REQ-ADM-008 | The system shall support feature flags to enable or disable capabilities without deployment. | Should | CAP-14 | Flag toggle test |
| REQ-ADM-009 | The system shall support approval workflows for refunds, payouts, supplier approval and fee changes. | Must | BR-009 | Approval chain test |
| REQ-ADM-010 | The system shall invalidate all sessions for a user when access is revoked. | Must | NFR-SEC-04 | Revocation test |
| REQ-ADM-011 | The system shall record the reason for every manual status override and surface overrides in a weekly report. | Must | BN-15 | Override report test |
| REQ-ADM-012 | The system shall restrict bulk personal-data export to named roles and require a second approval above a record threshold. | Should | BR-026 | Threshold approval test |

## 4.15 Reporting and analytics (REQ-RPT)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-RPT-001 | The system shall provide a daily operations dashboard for orders, payments, deliveries, exceptions and tickets. | Must | BN-24 | Dashboard completeness check |
| REQ-RPT-002 | The system shall report orders and gross order value by day, department, supplier and status. | Must | BN-19 | Report totals match ledger and orders |
| REQ-RPT-003 | The system shall report revenue, commission, delivery margin and contribution by department and period. | Must | BN-19 | Contribution calculation test |
| REQ-RPT-004 | The system shall report delivery performance by carrier, zone and supplier. | Must | BR-030 | Performance report test |
| REQ-RPT-005 | The system shall report returns by category, reason, supplier and outcome. | Must | BN-10 | Return report test |
| REQ-RPT-006 | The system shall provide a monthly supplier scorecard covering dispatch timeliness, cancellation, return and rating. | Must | BN-17 | Scorecard calculation test |
| REQ-RPT-007 | The system shall report payment reconciliation exceptions and ageing. | Must | BN-23 | Exception ageing report |
| REQ-RPT-008 | The system shall report customer repeat purchase and cohort retention where data volume permits. | Should | OBJ-08 | Cohort report test |
| REQ-RPT-009 | The system shall export reports as CSV with the filters applied. | Must | CAP-15 | Export matches screen |
| REQ-RPT-010 | The system shall state the data freshness timestamp on every report. | Should | BN-24 | Timestamp visible |

## 4.16 Reviews and ratings (REQ-REV)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-REV-001 | The system shall allow a review only from a customer with a delivered purchase of that line. | Must | BR-014 | Non-buyer review blocked |
| REQ-REV-002 | The system shall allow one review per purchased order line. | Must | BR-014 | Duplicate blocked |
| REQ-REV-003 | The system shall moderate reviews for abuse and personal data, not for disagreement. | Must | BR-014 | Moderation reason codes |
| REQ-REV-004 | The system shall allow a supplier to post one public reply per review. | Should | CAP-16 | Reply test |
| REQ-REV-005 | The system shall allow any user to report a review for abuse. | Should | CAP-16 | Report flow test |
| REQ-REV-006 | The system shall compute and display an average rating only when a minimum number of reviews exists. | Should | CAP-16 | Threshold display test |
| REQ-REV-007 | The system shall not allow a review to be edited after publication except for privacy removal. | Should | BR-014 | Edit blocked |

## 4.17 Promotions and vouchers (REQ-PRO)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-PRO-001 | The system shall allow an administrator to create a voucher with code, value, minimum basket, validity and usage limits. | Should | CAP-17 | Voucher creation test |
| REQ-PRO-002 | The system shall record the funding source of every discount: platform or supplier. | Must | BR-005 | Funder visible in ledger |
| REQ-PRO-003 | The system shall enforce eligibility and stacking rules at checkout. | Should | CAP-17 | Stacking rule test |
| REQ-PRO-004 | The system shall apply the discount to eligible lines and allocate it proportionally across suppliers. | Should | BR-004 | Allocation test |
| REQ-PRO-005 | The system shall attribute every redemption to a campaign for reporting. | Should | BN-21 | Campaign report |
| REQ-PRO-006 | The system shall enforce campaign budget caps and stop redemption when exhausted. | Could | CAP-17 | Cap test |
| REQ-PRO-007 | The system shall prevent supplier-funded discounts from reducing the supplier payable below zero without an explicit negative-balance rule. | Should | BR-029 | Negative balance test |

## 4.18 Brand and franchise configuration (REQ-FRN)

| ID | Requirement | Priority | Source | Verification |
|---|---|---|---|---|
| REQ-FRN-001 | The system shall store brand assets, trading name, contact details and policy text as configuration. | Must | BR-022 | Configuration change test |
| REQ-FRN-002 | The system shall store territory rules and display them where a territory restriction applies. | Should | BR-022 | Territory rule test |
| REQ-FRN-003 | The system shall store franchise or licence fee display rules and keep them inactive by default. | Must | BR-022, D-10 | Default state is inactive |
| REQ-FRN-004 | The system shall require a recorded licence reference before any franchise-branded configuration can be activated. | Must | D-10 | Activation blocked without reference |
| REQ-FRN-005 | The system shall record which brand configuration was active on each order for evidence. | Should | BN-20 | Order brand record |
| REQ-FRN-006 | The system shall produce a compliance report of brand and territory configuration changes. | Could | CAP-18 | Report generation test |

---

# 5. Use cases

## UC-01 Multi-supplier purchase and payment

**Actors:** Customer, PSP, system. **Trigger:** customer proceeds to checkout. **Preconditions:** at least one purchasable variant in the cart.

**Main flow**

1. Customer opens the cart; the system revalidates price and stock per line.
2. Customer enters or selects an address with a landmark.
3. System groups lines by supplier, quotes delivery per shipment and shows item value, delivery, discounts, any small-order fee and total.
4. Customer accepts terms and privacy notice; system records consent with version.
5. System creates the parent order, supplier orders and reservations, and requests payment from the PSP.
6. Customer completes payment in the PSP interface.
7. PSP sends a signed callback; system verifies the signature and queries the PSP status.
8. System marks payment captured, confirms the order and notifies customer and suppliers.
9. Each supplier accepts or rejects within the acceptance window.

**Alternates**

- 4a. Cart below minimum basket: system offers to add items or applies the disclosed small-order fee.
- 7a. Callback invalid: system rejects it, records the attempt and waits for the verified status.
- 7b. Payment fails: system releases reservations after the retry window, keeps the cart and notifies the customer.
- 9a. Supplier rejects: system cancels that supplier order, initiates a partial refund for its lines and delivery share, and continues the rest.

**Postconditions:** parent order exists with correct payment state; each supplier order has an owner and a state; ledger entries exist for payment and payables. **Requirements:** REQ-CHK-001 to 015, REQ-ORD-001 to 009, REQ-PAY-001 to 014.

## UC-02 Supplier onboarding and verification

**Actors:** Supplier applicant, operations, finance. **Trigger:** application submitted.

**Main flow**

1. Applicant submits business, owner and payout details and uploads documents.
2. System checks completeness, duplicates and document validity.
3. Operations reviews documents, conducts a site visit and records evidence.
4. Finance verifies the payout account name against the legal or trading name.
5. Operations approves, rejects or requests information, with a reason.
6. On approval, the contract version is recorded and the supplier can publish listings after moderation.

**Alternates**

- 2a. Duplicate TIN or bank account: application is held for review.
- 4a. Name mismatch: approval blocked until evidence is provided.
- 5a. Information requested: applicant corrects and resubmits the same record.

**Postconditions:** supplier state, evidence and decision are recorded and auditable. **Requirements:** REQ-KYC-001 to 014.

## UC-03 Listing creation and moderation

**Actors:** Supplier, moderator, category lead. **Trigger:** supplier submits a listing.

**Main flow**

1. Supplier selects a category; system presents the attribute template and checklist.
2. Supplier enters product, variants, SKU, price, stock, media and category attributes.
3. System validates mandatory fields, SKU uniqueness, brand claims and prohibited terms.
4. Listing enters the moderation queue with the category checklist.
5. Moderator approves, rejects or requests changes with reason codes.
6. Approved and in-stock listings become visible; rejected listings return to the supplier with reasons.

**Alternates**

- 3a. Mandatory attribute missing: submission blocked with field-level guidance.
- 5a. Suspected counterfeit or unsafe item: listing held and escalated to the category lead.
- 6a. Stock reaches zero after approval: listing is hidden automatically.

**Postconditions:** listing version, decision and reason are recorded. **Requirements:** REQ-CAT-001 to 016, REQ-INV-005.

## UC-04 Supplier fulfilment and dispatch

**Actors:** Supplier, operations, carrier. **Trigger:** supplier accepts an order.

**Main flow**

1. Supplier sees only its order lines and the delivery data needed to pack.
2. Supplier marks the order ready and records package count, weight and dimensions.
3. System creates shipment records and requests pickup or drop-off per the configured mode.
4. Supplier hands over parcels; waybill is recorded against each shipment.
5. Shipment status events are recorded until delivery and proof of delivery.

**Alternates**

- 2a. Item unavailable after acceptance: supplier requests a line cancellation with reason; system recalculates the order and refunds.
- 3a. Carrier does not arrive: operations reassigns or rebooks and records the failure.
- 4a. Waybill missing: shipment remains unbooked and is flagged for operations.

**Postconditions:** shipments exist with carrier, waybill and cost; supplier order reflects dispatch. **Requirements:** REQ-ORD-002 to 009, REQ-LOG-001 to 016.

## UC-05 Manual logistics booking and delivery

**Actors:** Operations, carrier, customer. **Trigger:** shipment ready for pickup.

**Main flow**

1. Operations selects carrier and service from the configured register and rate rules.
2. System shows the quoted cost and the customer delivery charge separately.
3. Operations books the pickup with the carrier and records the waybill and pickup date.
4. Status events are entered or imported as the parcel moves.
5. On delivery, operations or the carrier records proof of delivery.
6. System marks the shipment delivered and starts the return window.

**Alternates**

- 3a. Quoted cost exceeds the charged delivery amount beyond the threshold: operations escalates before booking.
- 5a. Delivery fails: reason is recorded and a retry is scheduled per policy.
- 5b. Parcel lost or damaged: claim is opened and the customer is refunded or replaced.

**Postconditions:** shipment timeline and POD exist; delivery performance is measurable. **Requirements:** REQ-LOG-002 to 015, REQ-ORD-006.

## UC-06 Return request and refund

**Actors:** Customer, support, supplier, finance. **Trigger:** customer requests a return within the window.

**Main flow**

1. System checks eligibility by delivery date, category and policy version.
2. Customer selects lines, quantity and reason and adds evidence.
3. System routes the request to support and, where policy allows, the supplier.
4. Decision is recorded: approved, partially approved or rejected, with reason.
5. Reverse pickup or drop-off is arranged and recorded.
6. Item is inspected where required.
7. System calculates the refund including the delivery share where applicable.
8. Finance approves above threshold; PSP processes the refund; ledger and supplier payable are updated.
9. Customer is notified and the return closes.

**Alternates**

- 1a. Outside window or non-returnable: request blocked with the policy explanation and a support link.
- 4a. Supplier contests: dispute is opened with evidence and escalated.
- 7a. Prior refund exists: calculation nets prior refunds and prevents over-refund.

**Postconditions:** refund recorded, supplier charged back where responsible, return closed with evidence. **Requirements:** REQ-RET-001 to 014, REQ-PAY-006 to 009.

## UC-07 Dispute resolution

**Actors:** Support, operations lead, finance, supplier, customer. **Trigger:** contested return, non-delivery or payment discrepancy.

**Main flow**

1. Dispute is opened with category, amount, evidence and affected lines.
2. System freezes the related supplier payable to the extent of the disputed amount.
3. Operations investigates using order, shipment and payment evidence.
4. Decision is recorded with reason and approver.
5. Resolution is executed: refund, release, replacement or rejection.
6. Hold is released or converted; both parties are notified.

**Alternates**

- 3a. Evidence insufficient: request more from the party and extend the timer once.
- 4a. Amount above delegated limit: founder approval required.

**Postconditions:** dispute closed with decision and financial effect. **Requirements:** REQ-RET-011 to 014, REQ-SET-005.

## UC-08 Supplier settlement and payout

**Actors:** Finance preparer, finance approver, supplier. **Trigger:** settlement cycle date.

**Main flow**

1. System calculates eligible payables: delivered, past return window, no holds.
2. System generates statements and a draft payout batch.
3. Preparer reviews exceptions and submits the batch.
4. A different approver reviews statements and exceptions and approves.
5. System exports the payout file and releases it to the channel.
6. Confirmations are reconciled; paid status and references are recorded.
7. Suppliers are notified and can view statements.

**Alternates**

- 1a. Open dispute or negative balance: payable is partially or fully held with a reason.
- 5a. Channel rejects a payment: item is flagged and retried in the next batch.
- 6a. Amount mismatch: exception is queued and the batch is not marked complete.

**Postconditions:** payout batch, approvals and reconciliation recorded. **Requirements:** REQ-SET-001 to 012.

## UC-09 Recall and safety suspension

**Actors:** Category lead, founder, support, customer. **Trigger:** recall notice, safety report or regulator instruction.

**Main flow**

1. Category lead identifies affected products, variants or batches.
2. Listing is suspended immediately and removed from sale.
3. Affected orders and buyers are identified.
4. Safety notice is sent to affected buyers with instructions.
5. Returns or refunds are handled outside normal eligibility where safety requires.
6. Supplier is notified and evidence is retained.

**Alternates**

- 2a. Supplier disputes the suspension: listing remains suspended pending review.
- 5a. Refund exceeds normal limits: founder approval with a safety reason code.

**Postconditions:** product unavailable, buyers informed, evidence retained. **Requirements:** REQ-CAT-009, REQ-NOT-008, REQ-RET-001.

## UC-10 Support ticket resolution

**Actors:** Customer, support agent, operations, finance. **Trigger:** customer contact by any channel.

**Main flow**

1. Agent creates or receives a ticket linked to an order where possible.
2. System shows order timeline, payment, shipment and prior contacts.
3. Agent classifies the issue and responds within the first-response target.
4. Resolution action is taken: information, refund request, return, carrier claim or escalation.
5. Resolution code is recorded and the customer is notified.
6. Satisfaction rating is requested.

**Alternates**

- 3a. Issue needs another team: ticket is assigned with context and SLA continues.
- 4a. Resolution needs approval: ticket waits in an approval state, not closed.

**Postconditions:** ticket closed with code and evidence; SLA measured. **Requirements:** REQ-CS-001 to 010.

---

# 6. User stories and acceptance criteria

Stories are grouped by actor. Acceptance criteria use Given/When/Then where the behaviour is subtle; otherwise a testable statement is given.

## 6.1 Customer

| ID | Story | Acceptance criteria |
|---|---|---|
| US-01 | As a customer, I want to buy items from several shops in one checkout so that I pay and track once. | Given three suppliers in the cart, when I pay, then one parent order and three supplier orders exist and I see one order with three progress rows. |
| US-02 | As a customer, I want to know the delivery cost before paying. | Delivery is shown per shipment and in the total before the payment step; changing the address recalculates it. |
| US-03 | As a customer, I want to see whether an item will fit before buying. | Fashion and baby listings show a size guide and size attributes; missing size blocks publication. |
| US-04 | As a customer, I want to return an item that does not fit. | Given delivery within 7 days, when I request a return with a fit reason, then the request is accepted and routed, and the policy terms shown match the category. |
| US-05 | As a customer, I want to know where my parcel is. | Tracking shows current shipment state, carrier, waybill and estimated date without internal notes. |
| US-06 | As a customer, I want a real person to help when something goes wrong. | A ticket created during support hours receives a human first response within four working hours. |
| US-07 | As a customer, I want to pay without creating an account. | Guest checkout completes with phone, name and address only, and consent is recorded. |
| US-08 | As a customer, I want to control marketing messages. | Withdrawing marketing consent stops promotional messages and does not stop order updates. |

## 6.2 Supplier

| ID | Story | Acceptance criteria |
|---|---|---|
| US-09 | As a supplier, I want to list my range without a laptop. | A listing with variants, price, stock and photos can be created on a phone; mandatory fields are indicated. |
| US-10 | As a supplier, I want to know what to pack and where it goes. | The supplier order shows only its lines, recipient name, phone, address and landmark, and a packing checklist. |
| US-11 | As a supplier, I want to be paid accurately and on time. | My statement lists orders, commission, refunds, adjustments and net payable, and matches the payout reference. |
| US-12 | As a supplier, I want to contest a return that is not my fault. | I can add evidence and open a dispute; the payable is held only to the disputed amount. |
| US-13 | As a supplier, I want to know how I am performing. | A monthly scorecard shows dispatch timeliness, cancellations, returns and rating, computed from system events. |
| US-14 | As a supplier, I want clear reasons when a listing is rejected. | Rejection includes a reason code and a note, and I can correct and resubmit the same listing. |

## 6.3 Operations and finance

| ID | Story | Acceptance criteria |
|---|---|---|
| US-15 | As an operator, I want to verify a supplier before they sell. | No listing can publish until KYC is approved, the contract is recorded and the payout name matches. |
| US-16 | As a moderator, I want a queue that tells me what to check. | Each listing shows its category checklist, mandatory attributes and flags; decisions require a reason. |
| US-17 | As an operator, I want to book a carrier manually and keep the same records an API would give. | Manual booking requires carrier, service, waybill, cost and pickup date, and creates the same shipment record as Mode B. |
| US-18 | As finance, I want to reconcile payments daily. | The reconciliation run matches PSP lines to ledger entries, queues exceptions and reports unmatched value. |
| US-19 | As finance, I want payouts approved by someone else. | A batch prepared by one user cannot be approved by the same user. |
| US-20 | As an operator, I want to stop a dangerous product immediately. | Suspending a listing removes it from sale at once and notifies affected buyers. |

## 6.4 Control and oversight

| ID | Story | Acceptance criteria |
|---|---|---|
| US-21 | As a founder, I want to see contribution by department. | The monthly report shows revenue, commission, delivery margin, refunds and contribution per department. |
| US-22 | As an auditor, I want to reconstruct a refund. | For any refund, the actor, reason, approver, amount, prior refunds and PSP reference are retrievable. |
| US-23 | As an administrator, I want to change fees without a deployment. | A commission change with an effective date applies only to orders after that date; prior orders keep their rule. |
| US-24 | As a founder, I want to decide at month 6 with evidence. | The review pack contains orders, repeat rate, delivery performance, returns, supplier retention and contribution. |

---

# 7. External interface requirements

## 7.1 Payment service provider

| Interface | Direction | Requirement |
|---|---|---|
| Payment initiation | Outbound | Create a payment for the parent order with amount, currency, reference and return URL; receive a PSP reference and redirect or prompt |
| Callback | Inbound | Accept signed status callbacks; verify signature, timestamp and reference; respond quickly and process asynchronously |
| Status query | Outbound | Query by PSP reference before finalising state |
| Refund | Outbound | Full or partial refund by PSP reference with an idempotency key |
| Settlement or payout | Outbound or file | Instruct supplier payouts in the agreed channel, or export a file for manual upload |
| Reconciliation file | Inbound | Daily file or API listing of transactions, fees, refunds and payouts |
| Error handling | Both | Timeouts, retries with backoff, dead-letter queue and alerting |

The platform must support replacing the PSP without changing order, ledger or settlement logic. Provider-specific fields are isolated in an adapter.

## 7.2 Carrier

| Operation | Requirement |
|---|---|
| Quote | Return a price and estimated transit time for a parcel and destination zone |
| Book | Create a booking and return a waybill and label reference |
| Cancel | Cancel a booking before pickup where the carrier allows |
| Track | Return status events with timestamps and location where available |
| Proof of delivery | Return recipient, timestamp, method and evidence reference |
| Claim | Open and track a claim for loss or damage |
| Manual fallback | Every operation has a manual recording path with the same fields |

No carrier is assumed. Usiri, if it becomes a carrier, uses the same adapter contract as any other provider.

## 7.3 Messaging

SMS through a Tanzanian-capable gateway; WhatsApp through an approved business provider; email for receipts and statements. Templates are versioned per language. Delivery reports update message status. Opt-out is honoured for marketing only.

## 7.4 Storage and media

Product images and KYC documents are stored in private object storage. Product media is served through signed, time-limited URLs or a CDN with derivative sizes. KYC documents are never publicly addressable and access is logged.

## 7.5 Address and location

Address capture is text-first with area, street, landmark and optional pin. The platform must not depend on a geocoding provider for checkout to work. A pin, where provided, is stored as a hint, not as the sole address.

## 7.6 Reporting and export

CSV exports for orders, payments, payouts, returns and catalogue. Exports respect the filters applied and are logged. No direct database access is provided to business users.

---

# 8. Data requirements

## 8.1 Entity overview

| Entity | Key data | Relationships |
|---|---|---|
| Customer | Phone, name, email, consent, status | Addresses, orders, tickets, reviews |
| Address | Recipient, phone, area, street, landmark, pin, instructions | Customer, orders |
| Supplier | Legal name, trading name, TIN, status, contract, payout account | Users, products, orders, statements |
| Supplier document | Type, file reference, expiry, verification status | Supplier |
| Category | Parent, name, attributes, checklist, return policy | Products |
| Product | Supplier, category, title, brand, description, status | Variants, media, reviews |
| Variant | SKU, option values, price, stock, barcode | Product, order items, reservations |
| Reservation | Variant, quantity, order reference, expiry | Variant, order |
| Parent order | Customer, totals, payment state, address snapshot | Supplier orders |
| Supplier order | Supplier, amounts, commission rule, state, payout date | Items, shipments, returns |
| Order item | Variant snapshot, title, price, quantity, discount, tax line | Supplier order |
| Shipment | Carrier, service, waybill, weight, dimensions, cost, state | Supplier order, events |
| Shipment event | Status, source, timestamp, raw reference | Shipment |
| Payment | PSP reference, amount, state, method | Parent order, refunds, ledger |
| Refund | Payment, amount, reason, approver, PSP reference | Payment, return |
| Ledger entry | Account, debit, credit, reference, period | Payment, refund, payout |
| Payout | Supplier, period, gross, deductions, net, state, approvals | Supplier, ledger |
| Return | Order item, quantity, reason, evidence, state | Supplier order, refund |
| Dispute | Return or order, amount, evidence, state, decision | Return, supplier order |
| Ticket | Customer, order, category, state, SLA, resolution code | Customer, order |
| Review | Order item, rating, text, moderation state | Product, supplier |
| Consent | Purpose, notice version, timestamp, source | Customer |
| Audit record | Actor, action, entity, before, after, reason, timestamp | All |
| Configuration | Key, value, effective dates, approver | Fees, zones, policies, brand |

## 8.2 Data rules

1. Order items snapshot title, SKU, variant description, unit price, discount, tax line and commission rule.
2. Money is integer TZS; rounding is applied once per calculation and the rule is recorded.
3. Personal data is masked by default in lists and exports; reveal requires permission and reason.
4. KYC documents are encrypted, access-logged and retained per legal advice.
5. Audit records are append-only; no application role can update or delete them.
6. Deletion anonymises personal fields while preserving financial and audit records.
7. Category attributes are data, not schema columns; adding a department must not require a migration of product tables.

The physical schema, indexes and retention schedule are defined in the database design document. This section defines business data obligations only.

---

# 9. Non-functional requirements

## 9.1 Performance and scale

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-P-01 | Customer pages load quickly on a mid-range Android phone on 4G | LCP at 75th percentile within 3.0 s | Lighthouse and field measurement |
| NFR-P-02 | Core read APIs respond quickly under pilot load | p95 within 500 ms, excluding third-party calls | Load test |
| NFR-P-03 | Write APIs complete predictably | p95 within 1,000 ms, excluding PSP or carrier latency | Load test and tracing |
| NFR-P-04 | Search returns relevant results at pilot catalogue size | p95 within 800 ms at 5,000 SKUs | Query benchmark |
| NFR-P-05 | A customer can complete checkout on a mid-range device | Median under 5 minutes including payment | Moderated usability test |
| NFR-P-06 | Product images are sized for mobile data | No image above 250 KB on listing pages; responsive derivatives | Page-weight audit |
| NFR-S-01 | The pilot supports bursts with headroom | 100 concurrent users and 10 checkouts per minute, 5x design headroom | Load test |
| NFR-S-02 | The schema supports growth without re-architecture | 10x SKUs and 5x order volume over pilot | Design review and synthetic data test |

## 9.2 Availability and reliability

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-A-01 | Catalogue, checkout and order APIs are available during support hours | 99.5% monthly, excluding announced maintenance | Uptime monitoring |
| NFR-R-01 | Payment and order operations survive retries without duplication | Idempotent initiation and callback; zero duplicate orders in test | Integration and chaos tests |
| NFR-R-02 | Data can be recovered after failure | RPO 15 minutes; RTO 4 hours | Restore drill |
| NFR-R-03 | Background jobs retry safely and surface dead letters | At-least-once delivery with idempotent handlers; alert on failures | Job failure injection |

## 9.3 Security

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-SEC-01 | Authentication, checkout and admin meet a recognised baseline | OWASP ASVS Level 2 for in-scope controls | Security review and penetration test |
| NFR-SEC-02 | Traffic is encrypted and secrets protected | TLS 1.2 or higher; managed secret store; no secrets in logs | Configuration review and scan |
| NFR-SEC-03 | Passwords and staff authentication resist compromise | Argon2id; MFA for staff and supplier owners | Code review and test |
| NFR-SEC-04 | Authorisation is enforced server-side on every request | Deny-by-default; tenant scoping; automated authorisation tests | Test suite and manual review |
| NFR-SEC-05 | Abuse is rate-limited | Login 5 per minute per IP; OTP 3 per 10 minutes per number; checkout 10 per minute per user | Configuration test |
| NFR-SEC-06 | Uploads cannot become an attack vector | Type and size limits; malware scan; private storage; signed access | Upload tests |
| NFR-SEC-07 | Dependencies and images are scanned before release | No known critical vulnerability in production artefacts | CI report |
| NFR-SEC-08 | Security headers and cookie attributes are enforced | HSTS, CSP, frame denial, SameSite cookies | Header scan |

## 9.4 Privacy and audit

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-PRIV-01 | Consent and privacy notices are recorded and enforceable | Versioned notice; consent per purpose; withdrawal honoured | Process and data audit |
| NFR-PRIV-02 | Personal data is minimised in logs and interfaces | No card data; PII masked by default; access logged | Log inspection and role tests |
| NFR-PRIV-03 | Data subject requests can be fulfilled | Export, correction and deletion within the statutory period to be confirmed | Tabletop exercise with counsel |
| NFR-AUD-01 | Sensitive actions are traceable | 100% of role, refund, payout, price and supplier-status changes logged with actor, reason and before/after | Audit coverage test |
| NFR-AUD-02 | Audit records resist tampering | Append-only storage; separate access; retention per legal advice | Design review and access test |

## 9.5 Maintainability and operability

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-M-01 | Critical modules have automated tests | At least 70% unit coverage on order, payment, commission and refund logic; integration tests for adapters | CI report |
| NFR-M-02 | Database changes are controlled | Versioned migrations; tested rollback; no manual production schema edits | Migration review |
| NFR-M-03 | Code and decisions are documented | Architecture decision records; API specification generated from source; runbooks | Documentation review |
| NFR-OBS-01 | Failures are visible before customers report them | Structured logs with request IDs; error tracking; payment-success and uptime alerts; dashboards | Incident drill |
| NFR-OPS-01 | Deployments are repeatable and reversible | One-command deploy; rollback within 15 minutes; no manual production edits | Deploy and rollback drill |
| NFR-SUP-01 | Support can find any order quickly | Order lookup by number, phone, supplier or tracking reference in under 30 seconds | Usability test with support staff |

## 9.6 Accessibility, localisation and compatibility

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-ACC-01 | Critical customer flows are usable with assistive technology | WCAG 2.1 AA for catalogue, cart, checkout and tracking | Accessibility audit |
| NFR-I18N-01 | The interface works in Swahili and English | Swahili default; all strings externalised; TZS formatting; no hard-coded copy | Content review and pseudo-localisation test |
| NFR-COMP-01 | The site works on the devices customers use | Current Chrome, Safari, Firefox and Android WebView; graceful degradation | Device lab and analytics |

---

# 10. State models

## 10.1 Payment

| From | Event | To | Authority |
|---|---|---|---|
| — | Checkout | Initiated | System |
| Initiated | PSP accepted | Pending | PSP |
| Pending | Verified capture | Captured | System after status query |
| Pending | Failure or expiry | Failed | System |
| Captured | Refund completed | Partially refunded or Refunded | Finance approval and PSP |
| Captured | Chargeback | Reversed or Disputed | Finance |
| Failed | Retry within window | Initiated | Customer |

## 10.2 Supplier order

| From | Event | To | Authority |
|---|---|---|---|
| — | Parent order paid | Awaiting acceptance | System |
| Awaiting acceptance | Supplier accepts | Accepted | Supplier |
| Awaiting acceptance | Supplier rejects or window expires | Cancelled | Supplier or system |
| Accepted | Supplier starts packing | Preparing | Supplier |
| Preparing | Package ready | Ready for pickup | Supplier |
| Ready for pickup | Carrier takes parcel | Dispatched | Operations or carrier event |
| Dispatched | POD recorded | Delivered | Carrier or operations |
| Delivered | Return window closes | Completed | System |
| Any pre-delivery | Cancellation approved | Cancelled | Supplier or operations, with reason |

## 10.3 Shipment

Draft → Booked → Picked up → In transit → Out for delivery → Delivered. Exceptions: Failed attempt → Retry scheduled or Returned to supplier; Lost; Damaged. Only carrier events or an authorised operator can move a shipment to Delivered, and a POD is mandatory.

## 10.4 Return

Requested → Under review → Approved or Rejected → In reverse transit → Received → Inspected → Refunded or Partially refunded → Closed. A contested decision moves to Disputed and may return to Approved or remain Rejected.

## 10.5 Dispute

Opened → Under review → Resolved for customer, Resolved for supplier, or Escalated → Closed. A dispute freezes the disputed amount of the supplier payable until closed.

## 10.6 Customer-facing summary

The summary is derived, never typed: **Processing** while any supplier order is awaiting acceptance or preparing; **Shipped** when all active supplier orders are dispatched; **Partially delivered** when some shipments are delivered and others are not; **Delivered** when all shipments are delivered; **Cancelled** when all supplier orders are cancelled; **Return in progress** when any return is open; **Refunded** when refunds cover the captured amount. The customer sees both the summary and the per-supplier detail.

## 10.7 Transition authority

| Transition | Who may perform | Evidence required |
|---|---|---|
| Mark supplier order accepted or rejected | Supplier owner or staff with permission | Reason for rejection |
| Mark ready for pickup | Supplier | Package count and weight |
| Mark dispatched | Operations or carrier event | Waybill |
| Mark delivered | Carrier event or operations | POD |
| Approve refund | Support within limit; finance above | Reason and approver |
| Release payout | Finance approver, not preparer | Batch review |
| Suspend listing or supplier | Moderator, category lead or operations lead | Reason code |
| Override a state | Operations lead only | Reason, logged and reported |

---

# 11. Business rule enforcement

| Rule group | Enforced in | Evidence |
|---|---|---|
| Order structure and snapshots (BR-001, BR-011) | Order service and database constraints | Order record and tests |
| Server-side pricing (BR-003) | Checkout calculation service | Tampering tests |
| Commission on net value (BR-004) | Settlement service | Calculation tests and statements |
| Separate money amounts (BR-005) | Ledger accounts and reports | Finance report |
| Refund limits (BR-027) | Refund service | Over-refund test |
| Payout holds and maker-checker (BR-007, BR-028, BR-029) | Settlement workflow | Approval tests |
| Catalogue visibility (BR-010, BR-015, BR-034) | Catalogue service and moderation workflow | Publish-block tests |
| Delivery evidence (BR-008, BR-016) | Shipment service | POD requirement |
| Return eligibility (BR-018, BR-035) | Returns service with policy configuration | Eligibility matrix tests |
| Variants and SKU (BR-033) | Catalogue and inventory | Variant checkout tests |
| Access and audit (BR-023, BR-026) | Authorisation layer and audit service | Authorisation and audit tests |
| Brand and franchise (BR-022) | Configuration service | Activation and effective-date tests |

A rule that cannot be enforced in software must be enforced by a documented operating control, and that control must be named in the test plan. "We will remember" is not a control.

---

# 12. Traceability

## 12.1 Objective to requirement

| Objective | Business needs | Requirement modules | Acceptance theme |
|---|---|---|---|
| OBJ-01 Demand | BN-01, BN-04, BN-05 | REQ-CHK, REQ-ORD, REQ-DIS, REQ-INV | Three-supplier checkout completes and is tracked as one order |
| OBJ-02 Delivery | BN-06, BN-11 | REQ-LOG, REQ-ORD, REQ-NOT | Every shipment has carrier, waybill, events and POD |
| OBJ-03 Trust | BN-09, BN-10, BN-12 | REQ-RET, REQ-CS, REQ-PAY | Return resolved with refund, chargeback and communication |
| OBJ-04 Supply | BN-02, BN-03, BN-17 | REQ-KYC, REQ-CAT, REQ-RPT | Verified supplier publishes approved variants and sees own data only |
| OBJ-05 Economics | BN-08, BN-19, BN-23 | REQ-SET, REQ-PAY, REQ-RPT | Commission, refunds and payouts reconcile to the ledger |
| OBJ-06 Compliance | BN-13, BN-15, BN-26 | REQ-ACC, REQ-ADM, REQ-NOT | Consent, terms version, invoices and audit are evidenced |
| OBJ-07 Operability | BN-12, BN-24, BN-27 | REQ-CS, REQ-RPT, REQ-ADM | A pilot day runs in the system without shadow spreadsheets |
| OBJ-08 Scale decision | BN-28, BN-25 | REQ-RPT | Month-6 pack shows demand, retention, delivery and contribution |

## 12.2 Rules of traceability

1. Every Must requirement references at least one business need and one verification method.
2. Every business rule marked Confirmed or Proposed has at least one requirement that enforces it or a named manual control.
3. Every test case references a requirement ID; a test without a requirement is either unnecessary or exposes a missing requirement.
4. The traceability matrix is a living file, updated in the same change as the requirement.
5. No requirement is deleted; it is marked withdrawn with a reason and a replacement reference.

---

# 13. Verification and acceptance

## 13.1 Test levels

| Level | Scope | Owner |
|---|---|---|
| Unit | Calculation, state transitions, validation | Engineering |
| Integration | PSP sandbox, carrier adapter stub, messaging, storage | Engineering |
| End-to-end | Customer, supplier, operations journeys on staging | QA and operations |
| Security | Authorisation matrix, input handling, callback forgery, dependency scan | Technical lead and reviewer |
| Performance | Load and soak at pilot targets with headroom | Engineering |
| Accessibility | WCAG 2.1 AA on critical flows | Design and QA |
| User acceptance | Real operators run scripted and exploratory pilot days | Founders and operations |
| Pilot acceptance | Live orders measured against objectives | Founders |

## 13.2 Entry and exit criteria

**Entry to system testing:** requirements baseline approved; environments available; PSP sandbox and carrier contract confirmed; test data prepared; no open critical defect.

**Exit to pilot:** all Must requirements verified; no open critical or high defect; reconciliation proven with seeded mismatches; restore drill passed; security review closed; legal memo received; supplier cohort and carrier ready; runbooks written.

## 13.3 Acceptance scenarios

| ID | Scenario | Primary requirements |
|---|---|---|
| AT-01 | A three-supplier order is paid, partially rejected, partially delivered and partially refunded, and the ledger balances. | REQ-CHK, REQ-ORD, REQ-PAY, REQ-SET |
| AT-02 | A supplier is rejected for a name mismatch, corrects the record and is approved without duplication. | REQ-KYC-004, REQ-KYC-008, REQ-KYC-013 |
| AT-03 | A fashion listing with size variants is rejected for a missing size guide, corrected and published. | REQ-CAT-002, REQ-CAT-013, REQ-CAT-008 |
| AT-04 | A payment callback is forged and rejected; the genuine callback is verified and the order proceeds once. | REQ-PAY-002, REQ-PAY-003, REQ-PAY-004 |
| AT-05 | A delivery fails twice, is returned to the supplier and the customer is refunded with the correct delivery treatment. | REQ-LOG-009, REQ-LOG-010, REQ-RET-008 |
| AT-06 | A beauty listing is reported as expired; the listing is suspended and affected buyers are notified. | REQ-CAT-009, REQ-NOT-008, REQ-RET-001 |
| AT-07 | A payout batch prepared by finance cannot be approved by the same person. | REQ-SET-006 |
| AT-08 | A customer requests deletion; personal fields are anonymised and financial records remain. | REQ-ACC-010 |
| AT-09 | A support agent resolves a ticket within SLA using only the console. | REQ-CS-001, REQ-CS-002, REQ-CS-004 |
| AT-10 | The daily reconciliation identifies a seeded amount mismatch and queues it. | REQ-PAY-010, REQ-PAY-011 |

---

# 14. Open issues

| ID | Issue | Impact | Owner | Needed by |
|---|---|---|---|---|
| D-13 | Exact department tree | Category configuration and templates | Founders | BRD sign-off |
| D-14 | Minimum basket or small-order fee | Checkout validation and conversion | Founders | Checkout freeze |
| D-15 | Category commission schedule | Settlement rules and supplier contracts | Founders and finance | Supplier contracts |
| D-16 | Beauty authenticity evidence | Listing requirements and moderation | Category lead | Beauty go-live |
| D-17 | Baby safety declaration | Listing requirements and liability | Founders | Baby go-live |
| D-18 | Fashion return policy | Return eligibility and refunds | Founders | Policy publication |
| D-19 | Launch supplier cohort | Launch readiness | Founders | Recruitment plan |
| D-20 | Timeline fallback | Roadmap and scope gate | Founders and CTO | Roadmap sign-off |
| O-03 | PSP selection and contract | Payment adapter and settlement | Finance lead | Before payment build |
| O-04 | Carrier selection and terms | Logistics adapter and rates | Operations lead | Before logistics build |
| O-09 | Tax treatment, invoicing and withholding | Receipts, statements, VAT lines | Accountant and counsel | Before launch |
| O-14 | Hosting region and data location | Architecture and compliance | CTO and counsel | Before architecture sign-off |
| O-10 | PDPA registration, DPO, retention and cross-border position | Deletion, archive and transfer design | Counsel | Before launch |

A TBC value in this specification is not a defect. It is a controlled unknown that must be resolved before the related requirement is built, and the resolution must be recorded in the decision log.

---

# Appendix A. Requirement index

| Module | Prefix | Count | Primary business needs |
|---|---|---|---|
| Identity and consent | REQ-ACC | 12 | BN-13, BN-14 |
| Supplier onboarding | REQ-KYC | 14 | BN-02, BN-17 |
| Catalogue and moderation | REQ-CAT | 16 | BN-03, BN-16, BN-18 |
| Inventory | REQ-INV | 9 | BN-05 |
| Discovery | REQ-DIS | 10 | BN-04, BN-26 |
| Cart and checkout | REQ-CHK | 15 | BN-01, BN-06 |
| Orders | REQ-ORD | 14 | BN-01, BN-09, BN-11 |
| Payments | REQ-PAY | 14 | BN-07, BN-23 |
| Settlement | REQ-SET | 12 | BN-08, BN-23 |
| Logistics | REQ-LOG | 16 | BN-06, BN-11 |
| Returns and disputes | REQ-RET | 14 | BN-09, BN-10 |
| Support | REQ-CS | 10 | BN-12 |
| Notifications | REQ-NOT | 9 | BN-11, BN-18 |
| Administration | REQ-ADM | 12 | BN-14, BN-15 |
| Reporting | REQ-RPT | 10 | BN-19, BN-24, BN-28 |
| Reviews | REQ-REV | 7 | BN-22 |
| Promotions | REQ-PRO | 7 | BN-21 |
| Brand and franchise | REQ-FRN | 6 | BN-20 |

Total: 207 requirements, of which the Must set forms the launch scope.

# Appendix B. Glossary

Terms are as defined in the BRD, with these software additions:

| Term | Meaning |
|---|---|
| Idempotency key | A client or system reference that makes a repeated operation return the original result instead of repeating the effect |
| Dead letter | A failed background job set aside for inspection after retries |
| Derived state | A state computed from events rather than stored as an editable field |
| Adapter | An isolated integration component that translates between the platform and an external provider |
| Tenant scoping | Restricting every query and action to the organisation a user belongs to |
| Snapshot | A stored copy of values at transaction time, unaffected by later edits |
| Effective dating | A configuration rule that applies from a date and leaves history unchanged |
| Break-glass | Temporary elevated access with a reason, alerting and review |
