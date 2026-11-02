# 0. Document control

| Field | Value |
|---|---|
| Document | Business Requirements Document |
| Project | Usiri Marketplace (working name) |
| Document ID | UM-BRD-001 |
| Version | 1.0 |
| Status | **Draft for founder review. No implementation is authorized.** |
| Date | 30 October 2026 |
| Prepared for | The founding group |
| Prepared by | Project initiator, acting as business analyst and software architect |
| Classification | Confidential — internal discussion |
| Baseline | UM-DISC-001 Requirements Discovery Report v0.2; UM-AMD-001 Scope Amendment v1.0; UM-DEC-001 Decision Log v0.2 |
| Next document | UM-SRS-001 Software Requirements Specification |

> **Status notice.** Usiri Group of Companies is a **potential** logistics and brand partner. No approval, API, rate card, franchise term or brand licence is assumed. The platform is designed to work with any qualified carrier and any licensed payment service provider. No code has been written.

## 0.1 How this document is used

The BRD states **what the business needs and why**, in business language. It does not prescribe screens, schemas or endpoints; those belong to the SRS, the architecture and the UX specification. Every business need carries an ID so that the SRS and the test plan can trace back to it. Evidence labels follow the discovery report: **[Confirmed]**, **[Assumption]**, **[Proposed]**, **[Open]**.

---

# 1. Executive summary

The proposed marketplace lets customers in Dar es Salaam buy from many verified suppliers in one checkout, pay through a licensed payment provider, and receive a tracked delivery. Suppliers keep their stock and their shop; the platform supplies demand, catalogue discipline, delivery coordination, payment reconciliation and customer care. The platform earns commission on completed merchandise and a coordination margin on delivery. It does not buy inventory, hold customer funds or operate a fleet.

The founders decided on 30 October 2026 to launch with **general merchandise**, bounded to six departments, rather than the narrower home-and-kitchen pilot originally recommended. The decision increases the size of the opportunity to be tested and increases the operational load: variants, category attributes, category-specific returns, authenticity controls and higher moderation volume all become launch requirements.

The business test is narrow and measurable. Within six months of launch the platform must show that customers will buy across suppliers, that delivery can be trusted, that failures are resolved fairly, that suppliers stay, and that each order contributes a positive margin. If those five things are not true, the platform should change or stop; it should not scale.

This document defines the business requirements for that test. It is the basis for the SRS, the architecture and the test plan, and it records what remains unresolved.

---

# 2. Business context

## 2.1 The problem being solved

A customer in Dar es Salaam who wants a set of household, fashion or baby items faces a fragmented market. She must visit several shops or several Instagram and WhatsApp sellers, negotiate delivery separately, pay without a receipt, and accept that a wrong size or a damaged item may not be exchangeable. A small supplier faces the mirror image: reach depends on foot traffic or on social media effort, delivery is ad hoc, and there is no affordable way to look trustworthy to a new customer.

The marketplace addresses both sides with one promise: **many verified shops, one checkout, one delivery coordination point, and a return path that works**.

## 2.2 What is known and what is not

| Area | What the evidence supports | What remains unproven |
|---|---|---|
| Demand | Urban households buy these categories online and through social commerce; competitors operate in Dar es Salaam | Willingness to buy across suppliers in one basket; sensitivity to a minimum basket |
| Supply | Small and medium shops exist in the target categories and lack digital reach | Willingness to accept commission, payout delay and catalogue discipline |
| Delivery | Licensed couriers operate in the city; address quality is uneven | Cost per parcel by category; first-attempt success; liability terms |
| Payments | Mobile money is dominant; licensed PSPs serve merchants | PSP settlement product, fees and refund behaviour |
| Usiri | A logistics and brand business exists | Any partnership, API, rate card or licence |

The concept document, the discovery report and the workbook hold the supporting detail. This BRD does not upgrade any assumption into a fact.

## 2.3 Why a managed marketplace rather than a shop or a reseller

A managed marketplace keeps capital light and lets the platform test demand across categories without owning stock. It also creates a trust role that a classifieds site does not: the platform verifies suppliers, moderates listings, coordinates delivery, and stands behind the return process. That trust role is the product. It is also the cost centre, which is why the operating model must be explicit about who does what.

## 2.4 What "general merchandise" means in this project

It means a **multi-department consumer assortment of six bounded departments**, not an unlimited catalogue:

1. Homeware, storage and kitchenware
2. Small kitchen and home appliances
3. Fashion and footwear
4. Beauty and personal care
5. Baby and maternity
6. Home and kitchen bundles

Consumer electronics and phones, groceries, furniture, building materials and restricted goods are excluded from launch. The boundary is a condition of a safe launch. It is recorded in UM-AMD-001 and is a founder decision, not a vendor preference.

---

# 3. Business objectives and success measures

## 3.1 Objectives

| ID | Objective | Why it matters | Measure and target | Review |
|---|---|---|---|---|
| OBJ-01 | Prove that customers will buy from several verified suppliers through one checkout | Demand is the first risk; without orders nothing else can be tested | 900 completed orders in pilot month 6; at least 30% of orders contain two or more suppliers | Monthly |
| OBJ-02 | Deliver reliably enough that customers trust the platform with repeat purchases | A late or lost parcel destroys trust faster than price attracts it | At least 90% on-time delivery; first-attempt success at least 80% | Weekly |
| OBJ-03 | Resolve failures fairly and quickly | The first exception is the moment of truth | 90% of complaints resolved within 48 hours; returns below 5% of delivered orders | Weekly |
| OBJ-04 | Recruit and retain credible suppliers | Supply quality determines catalogue quality and returns | 40 verified suppliers by month 3; 80% retention after 90 days | Monthly |
| OBJ-05 | Prove positive contribution economics | Growth on negative unit economics destroys the company faster | Contribution at least 4% of gross order value by month 6 | Monthly |
| OBJ-06 | Operate within Tanzanian law and the platform's contracts | A compliance failure can stop trading and damage the brand | Written legal baseline; registrations and filings completed as advised | Before launch |
| OBJ-07 | Run the pilot with a small team without operational chaos | The team, not the software, is the constraint at launch | Every pilot order handled through the system; no shadow spreadsheets for money | Weekly |
| OBJ-08 | Produce evidence for a scale, pivot or stop decision | The pilot exists to buy information, not to prove a point | Documented go/no-go review at month 6 | Month 6 |

## 3.2 Guardrails

The objectives are not to be met by trading away the foundations:

- **No order without a verified supplier.** Growth in supplier count never outpaces verification capacity.
- **No delivery promise without a carrier commitment.** The promise is set from measured performance, not ambition.
- **No customer money outside the PSP.** The platform does not hold funds, lend, or operate a wallet.
- **No commission before the customer is served.** Revenue is recognised on completed merchandise, not on captured payment.
- **No silent exception.** Every manual override, refund, payout hold and safety suspension carries an actor, a reason and a record.

## 3.3 Measurement discipline

Targets in this document are **hypotheses to be baselined**, not commitments. The first four weeks of operation establish the baseline for conversion, basket size, delivery success, return rate and support volume. Targets are then reviewed against that baseline at the first monthly business review, and any change is recorded in the decision log. Vanity metrics — page views, app installs, follower counts — are not acceptance measures.

---

# 4. Scope

## 4.1 In scope for the first release

- A mobile-first customer web experience in Swahili and English, with guest checkout and optional accounts.
- A catalogue of six departments with product variants, category attributes, size guides, moderation and category-specific return rules.
- A supplier portal for onboarding, documents, catalogue, stock, orders, dispatch, statements and performance.
- An operations console for verification, moderation, orders, payments, payouts, logistics, returns, disputes, support and reporting.
- A logistics coordination capability that works manually at launch and is provider-agnostic.
- Payment through a licensed PSP with verification, refunds, reconciliation and supplier payouts.
- Category-sensitive returns and a support workflow with order context.
- Role-based access, audit logging, configuration, and the legal pages required at checkout.

## 4.2 Launch profile

| Dimension | Launch position | Basis |
|---|---|---|
| City | Dar es Salaam mainland | [Confirmed] |
| Currency and tax | TZS; tax treatment configurable and unresolved | [Assumption] / [Open] |
| Departments | Six bounded departments | [Confirmed] D-01 |
| Suppliers | 40 verified at launch; 60 by month 6 | [Assumption] |
| Active SKUs | 800–1,200 | [Assumption] |
| Orders | 900 completed orders in month 6 | [Assumption] |
| Commission | 8% hypothesis, configurable and effective-dated | [Assumption] |
| Delivery charge | TZS 5,000 hypothesis, category and zone aware | [Assumption] |
| Minimum basket | TZS 30,000 or a small-order fee, to be tested | [Open] D-14 |
| Support | 09:00–18:00 Monday–Saturday | [Proposed] |

## 4.3 Out of scope for the first release

Native mobile applications; marketplace warehouse or dark store; marketplace fleet; real-time GPS tracking; customer wallet, credit or instalments; buyer-seller chat; multi-city operations; international shipping and multi-currency; AI recommendations; automated supplier payouts; microservices and event streaming; advertising auction and loyalty programme.

## 4.4 Scope change rule

A capability enters the first release only if it is required to complete, deliver, refund or support a pilot order, or to meet a legal obligation. Everything else is deferred, however attractive. Any exception requires a written change note approved by the founders, with the schedule or quality consequence stated.

---

# 5. Stakeholders and roles

## 5.1 Stakeholder register

IDs STK-01 to STK-16 follow UM-DISC-001. STK-17 to STK-19 are added by this BRD for commercial parties that the baseline treats as dependencies rather than users.

| ID | Stakeholder | What they need | What the platform needs from them |
|---|---|---|---|
| STK-01 | Guest visitor | Browse and understand price, delivery and returns before committing | Lawful use; accurate contact details at checkout |
| STK-02 | Registered customer | Reliable purchase, tracking, returns and help | Accurate address and contact; payment |
| STK-03 | Individual merchant | More sales without a delivery desk | Accurate listings, current stock, standard packing |
| STK-04 | Business supplier | A predictable channel that protects its reputation | Contract compliance, quality, fulfilment discipline |
| STK-05 | Supplier employee | Clear daily tasks without sensitive data | Correct packing and dispatch updates |
| STK-06 | Logistics provider | Profitable, predictable parcel volume | Pickup, line-haul, delivery, status events, claims |
| STK-07 | Logistics agent or driver | Clear stops and proof of delivery | Delivery, status events, proof of delivery |
| STK-08 | Customer support agent | Full context to resolve issues | Fair, documented decisions |
| STK-09 | Finance personnel | Accurate money and clean reconciliation | Timely review and approval |
| STK-10 | Catalogue moderator | A trustworthy, accurate catalogue | Consistent review against the checklist |
| STK-11 | Operations administrator | Orders move and exceptions close | Timely booking and exception handling |
| STK-12 | Super administrator | The platform is controlled and auditable | Least-privilege discipline |
| STK-13 | Franchise or brand manager | Brand standards and licence compliance | Nothing until a written licence exists |
| STK-14 | Technology administrator | A secure, available system | Patch, monitor and restore discipline |
| STK-15 | Auditor or adviser | Evidence that controls work | Independent review |
| STK-16 | Regulators and authorities | Compliance with applicable law | Registration and cooperation |
| STK-17 | Payment service provider | Compliant merchants and clean transaction data | Contractual compliance; accurate references |
| STK-18 | Usiri, potentially | A credible operating partner and brand licensor | Nothing is assumed until a written agreement |
| STK-19 | Investors or lenders, potentially | Evidence of traction and unit economics | Nothing is assumed |

## 5.2 Internal role model

Fourteen roles are defined in the discovery report (ROL-01 to ROL-14). For business purposes they collapse into five accountability groups:

| Group | Roles | Accountable for |
|---|---|---|
| Customer-facing | Guest, customer | Their own account and orders |
| Supply-facing | Supplier owner, supplier staff | Their own catalogue, stock and fulfilment |
| Logistics-facing | Carrier administrator, agent or driver | Assigned shipments and delivery evidence |
| Platform operations | Support, moderator, category lead, operations lead | Catalogue quality, customer resolution, delivery coordination |
| Control functions | Finance, administrator, auditor, founder | Money, access, audit and direction |

## 5.3 Decision rights

| Decision | Recommends | Approves | Informed |
|---|---|---|---|
| Supplier approval and suspension | Operations lead | Founder | Finance |
| Listing approval and rejection | Moderator | Category lead | Supplier |
| Refund within limit | Support agent | Finance | Customer |
| Refund above limit | Finance | Founder | Customer |
| Payout batch | Finance preparer | Second finance approver or founder | Suppliers |
| Carrier selection and rates | Operations lead | Founder | Finance |
| Commission and fee change | Founder | Founder | Suppliers, finance |
| Category addition or removal | Category lead | Founder | Operations, finance |
| Brand or franchise configuration activation | Founder | Written licence holder | All staff |
| Safety recall and listing suspension | Category lead | Founder or duty manager | Customers affected, supplier |

Separation of duties is a requirement, not a preference: the person who prepares a payout does not approve it, and the person who approves a listing does not verify the supplier's bank account.

---

# 6. Target operating model

## 6.1 Supply

Suppliers hold their own stock and pack their own orders. The platform verifies the supplier's identity, business registration, tax registration, shop location and payout account before the first listing is approved. Verification is re-performed on a schedule and on any change of ownership or bank account. Suppliers receive a portal, a packing standard, a performance scorecard and a settlement statement.

The platform does not buy stock, set prices unilaterally, or take ownership of inventory. It does set listing standards, commission, delivery charges and service levels, and it can suspend a listing or a supplier for safety, fraud or repeated failure.

## 6.2 Demand

Demand is generated through search, category browsing, supplier storefronts and controlled promotions. The customer experience is mobile-first and Swahili-first. Guest checkout is allowed because registration friction is a known cause of abandonment in the market; an account is offered after the first order. Reviews come only from verified purchasers.

## 6.3 Order and delivery

One checkout creates one parent order and one supplier order per supplier. Each supplier order is fulfilled separately and may ship separately, so a three-supplier basket produces up to three parcels. The customer sees one order with a per-supplier progress view, not three unrelated orders.

The platform coordinates pickup through licensed carriers. At launch the coordination is manual (Mode A): an operator books the carrier, records the waybill, and updates status from carrier messages. The data recorded is identical to what an integrated carrier would supply, so an API can be added later without changing the order model. Delivery charges are quoted per shipment, displayed before payment, and allocated to the supplier order that generated them.

## 6.4 Money

A licensed PSP collects the customer's payment. The platform records a payable to each supplier equal to merchandise value less commission and less any supplier-funded discount, and a separate carrier payable. The supplier payable becomes eligible for payout after delivery plus the return window, subject to holds for disputes, negative balances or KYC issues.

The platform's own revenue is commission plus the coordination margin between the customer delivery charge and the carrier charge. Pass-through money is never counted as revenue. No customer funds are held outside the PSP, and the platform is not described as an escrow service.

## 6.5 Service

Customer support runs during published hours and works from order context, not from memory. Every ticket links to an order, a supplier order and, where relevant, a shipment. Refunds above a threshold require finance approval. The support standard is a first human response within four working hours and resolution of 90% of complaints within 48 hours.

## 6.6 Catalogue and category management

Each department has a category lead — initially a founder or the operations lead wearing a category hat — who owns the assortment, the attribute template, the moderation checklist and the return rules. Moderation is a queue with reasons and resubmission, not an inbox. Listings are audited after publication, and a prohibited-item list is maintained as configuration.

The platform deliberately runs a **shallow but credible** catalogue: the best-selling, photographable, returnable range of each supplier, not its entire inventory. Depth is added after the first cohort proves it can list and fulfil well.

## 6.7 Capacity assumptions

The launch team is one operations lead, one part-time moderator, one support agent (shared with operations), one finance person (part-time) and the technical team. That capacity supports roughly 40 suppliers and 1,000 listings only if onboarding is phased. The business plan must not assume the same team can double supplier count without adding moderation capacity.

---

# 7. Business processes

| ID | Process | Trigger | Outcome | Owner |
|---|---|---|---|---|
| WF-01 | Customer purchase across suppliers | Customer checks out | Paid parent order with supplier orders and reservations | Operations |
| WF-02 | Supplier fulfilment | Supplier order accepted | Packed parcel handed to carrier with waybill | Supplier |
| WF-03 | Payment verification and reconciliation | PSP callback or daily file | Payment matched to order; exceptions queued | Finance |
| WF-04 | Manual logistics (Mode A) | Supplier marks ready for pickup | Shipment booked, tracked and delivered with POD | Operations |
| WF-05 | Integrated logistics (Mode B) | Carrier API available | Same records created through the adapter | Operations |
| WF-06 | Returns, refunds and disputes | Customer request within window | Item returned or refund decided; supplier charged back | Support and finance |
| WF-07 | Supplier onboarding and KYC | Supplier application | Verified supplier able to publish approved listings | Operations |
| WF-08 | Support and escalation | Customer contact | Ticket resolved or escalated with a documented decision | Support |

Process detail, including alternative paths and exception handling, is in the SRS use cases. The business rules that govern each process are in Section 9.

---

# 8. Business needs catalogue

Each need is a business outcome. The SRS converts it into testable software requirements.

| ID | Business need | Capabilities | Success measure |
|---|---|---|---|
| BN-01 | A customer can buy from several suppliers in one checkout and see one order | CAP-06, CAP-07 | Multi-supplier orders complete without manual intervention |
| BN-02 | Only verified, accountable suppliers can sell | CAP-02 | 100% of live suppliers have complete KYC evidence |
| BN-03 | Products are described consistently enough to compare and return | CAP-03 | 95% of listings pass attribute completeness at first review |
| BN-04 | Customers can find products quickly on a phone | CAP-05 | Search success rate and zero-result rate monitored |
| BN-05 | Price and stock shown are true at the moment of payment | CAP-04 | Oversell rate below 0.5% of orders |
| BN-06 | Delivery cost and promise are clear before payment | CAP-10 | Delivery-related complaints below 5% of orders |
| BN-07 | Payment is safe, verifiable and refundable | CAP-08 | 100% of payments matched or exceptioned within one day |
| BN-08 | Suppliers are paid correctly and on time | CAP-09 | Payout disputes below 1% of statements |
| BN-09 | A partially fulfilled order is handled without cancelling the whole order | CAP-07 | Partial cancellation and partial delivery supported end to end |
| BN-10 | Returns follow category rules that are fair and published | CAP-11 | Return decisions consistent with policy in audit sample |
| BN-11 | Customers know where their parcel is | CAP-07, CAP-13 | Tracking visible for 100% of shipments |
| BN-12 | A customer can reach a human with order context | CAP-12 | First response within four working hours |
| BN-13 | Personal data is collected lawfully and minimally | CAP-01, CAP-14 | Consent evidence for 100% of accounts |
| BN-14 | Each role sees only what its job requires | CAP-01, CAP-14 | Authorisation tests pass for every role |
| BN-15 | Sensitive actions are reconstructable after the fact | CAP-14 | 100% of refunds, payouts and status changes audited |
| BN-16 | Moderation capacity matches catalogue growth | CAP-03 | Queue age under 48 hours during onboarding |
| BN-17 | Supplier performance is measured objectively | CAP-15 | Scorecards available monthly to every supplier |
| BN-18 | A unsafe or recalled product can be removed and buyers notified | CAP-03, CAP-13 | Recall executed within one working day |
| BN-19 | Category profitability is visible | CAP-15 | Contribution reported by department monthly |
| BN-20 | Brand and franchise rules can be configured without code | CAP-18 | Configuration change without deployment |
| BN-21 | Promotions are controlled and funded deliberately | CAP-17 | Every discount attributable to a campaign and a funder |
| BN-22 | Reviews are trustworthy | CAP-16 | Only verified purchases published |
| BN-23 | Money reconciles to the ledger every day | CAP-08 | Unmatched transactions below 0.5% |
| BN-24 | Management can run the business from reports, not spreadsheets | CAP-15 | Daily operating report used at stand-up |
| BN-25 | The platform can grow without re-architecture | NFR-S-01, NFR-S-02 | 10x SKUs supported in design review |
| BN-26 | The experience works in Swahili and English | NFR-I18N-01 | No untranslated string in critical flows |
| BN-27 | The business can recover from data loss or outage | NFR-R-02 | Restore drill within target |
| BN-28 | Founders can decide to scale, pivot or stop on evidence | CAP-15 | Month-6 review pack complete |

---

# 9. Business rules

The full rule catalogue is BR-001 to BR-040, held in the discovery report and the scope amendment. The BRD groups them by the business question they answer.

## 9.1 Orders and pricing

| Rule | Statement | Status |
|---|---|---|
| BR-001 | One checkout creates one parent order and one supplier order per supplier | Proposed |
| BR-003 | Prices and totals are calculated server-side; the browser total is never authoritative | Proposed |
| BR-011 | Placing an order snapshots title, SKU, price, tax line and commission rule | Proposed |
| BR-012 | Cancellation is allowed before supplier acceptance; afterwards it becomes a return | Proposed |
| BR-019 | Money is stored as integer TZS with explicit rounding applied once | Proposed |
| BR-038 | A minimum delivered order value or small-order fee may apply, displayed before checkout | Open |

## 9.2 Money and settlement

| Rule | Statement | Status |
|---|---|---|
| BR-004 | Commission is charged on net completed merchandise, not gross captured payment | Proposed |
| BR-005 | Customer delivery charge, carrier charge and coordination fee are separate amounts | Proposed |
| BR-006 | Refunds may include item value and delivery share; change-of-mind refunds may exclude delivery | Open |
| BR-007 | Supplier payout is held until delivery plus the return window, extended by dispute or risk | Proposed |
| BR-009 | Every financial adjustment needs a reason, an actor and a second approver above threshold | Proposed |
| BR-021 | The platform is not an escrow or deposit-taking service and holds no customer funds | Confirmed |
| BR-027 | A refund cannot exceed captured amount less prior refunds and reversals | Proposed |
| BR-028 | A payout batch needs a preparer and a different approver | Proposed |
| BR-029 | Payouts may be held for open dispute, negative balance or unresolved KYC, with a written reason | Proposed |

## 9.3 Catalogue and supply

| Rule | Statement | Status |
|---|---|---|
| BR-010 | A product is visible only after moderation approval and while stock is above zero | Proposed |
| BR-013 | A supplier sees only the customer data needed to pack and hand over | Proposed |
| BR-015 | Prohibited items are blocked at listing and removed at moderation; relisting leads to suspension | Proposed |
| BR-022 | Brand, territory, fee and approval rules are configuration with effective dates | Confirmed |
| BR-033 | Every purchasable item resolves to a variant with its own SKU, price and stock | Proposed |
| BR-034 | A listing cannot publish until mandatory category attributes are complete | Proposed |
| BR-036 | Beauty listings require authenticity evidence and, where applicable, batch or expiry data | Proposed |
| BR-037 | Baby and maternity listings require safety declarations, age grading and recall checks | Proposed |
| BR-039 | Category commission rates may differ, but a rate change applies only to future orders | Proposed |
| BR-040 | A recall can suspend a listing and notify affected buyers without deleting order history | Proposed |

## 9.4 Delivery and returns

| Rule | Statement | Status |
|---|---|---|
| BR-008 | A supplier cannot mark an order delivered; delivery needs carrier or operations evidence | Proposed |
| BR-016 | Every shipment records carrier, service, waybill, cost, weight, dimensions, events and POD | Proposed |
| BR-017 | Failed attempts follow a published retry policy with customer contact before retry | Proposed |
| BR-018 | The return window starts at delivery and excludes hygiene or safety items where law allows | Open |
| BR-030 | Carrier and supplier performance is measured from system events and visible to the party | Proposed |
| BR-031 | A shipment can be run manually with the same records an API carrier would use | Confirmed |
| BR-035 | Return eligibility and refund treatment are category-specific and published before purchase | Open |

## 9.5 Trust, access and compliance

| Rule | Statement | Status |
|---|---|---|
| BR-014 | Only verified purchasers may review, once per purchased line, moderated for abuse | Proposed |
| BR-020 | VAT and tax lines are stored per invoice line and configurable; no treatment is assumed | Open |
| BR-023 | Audit records are append-only and cannot be edited through the application | Proposed |
| BR-024 | Personal data is collected for a stated purpose and deleted or anonymised on schedule | Proposed |
| BR-025 | Marketing consent is separate from transactional messages and withdrawable | Proposed |
| BR-026 | Staff access outside normal duties needs a reason, is time-bound and logged | Proposed |
| BR-032 | A customer can obtain a human response within published support hours | Proposed |

Rules marked **Open** cannot be implemented as fixed policy. They are configurable, and the default is the most protective position that is commercially tolerable. Each open rule has an owner in the decision log.

---

# 10. Information requirements

## 10.1 Core business entities

| Entity | Business meaning | Owner | Retention |
|---|---|---|---|
| Customer | A person who buys, with contact, addresses and consent | Platform | Active plus statutory period |
| Supplier | A verified seller with legal identity, contract and payout account | Platform | Contract plus statutory period |
| Supplier document | Registration, TIN, identity, site evidence, bank verification | Operations | As required by law and audit |
| Product and variant | What is sold, with attributes, media, price and stock | Supplier, moderated by platform | Life of listing plus order history |
| Parent order | The customer's commercial order | Platform | Statutory period |
| Supplier order | The supplier's obligation and settlement unit | Platform | Statutory period |
| Shipment | The physical movement of goods with carrier and proof | Platform | Statutory period |
| Payment and refund | Money received and returned through the PSP | Finance | Statutory period |
| Ledger entry | Every financial movement, with accounts and references | Finance | Statutory period |
| Payout | A batch payment to a supplier with approval evidence | Finance | Statutory period |
| Return and dispute | A claim, its evidence and its resolution | Support | Statutory period |
| Ticket | A customer contact and its resolution | Support | Policy period |
| Consent record | What was agreed, when, to which notice version | Platform | As required |
| Audit record | Who changed what, when and why | Platform | As required |

## 10.2 Information qualities

- **Single source of truth.** Money is recorded in the ledger; order status is derived from events, not typed into a field.
- **Snapshot at transaction.** Order lines preserve what was sold at the price and terms agreed.
- **Minimisation.** The supplier sees delivery data, not customer history; the carrier sees the address, not the price.
- **Traceability.** Every financial and access event can be reconstructed from records.
- **Separation.** Customer funds, platform revenue and supplier payables are distinct accounts.

## 10.3 Reporting needs

Daily: orders, payments, exceptions, deliveries due, tickets open, payouts due. Weekly: delivery success, returns, supplier dispatch performance, catalogue queue. Monthly: contribution by department, supplier cohort retention, customer repeat rate, category mix, moderation throughput.

---

# 11. Legal and regulatory obligations

| Area | Obligation in business terms | Status |
|---|---|---|
| Data protection (PDPA 2022, PDPC) | Lawful basis, notice, consent, access and deletion, security, registration where required | Counsel to confirm; REG-01 |
| Consumer contracts (FCC Standard Form Regulations 2014) | Fair standard-form terms, clear pricing, complaint handling | Counsel to confirm; REG-02 |
| Electronic transactions (ETA 2015) | Electronic records, signatures and evidence | Counsel to confirm; REG-03 |
| Payment services (Bank of Tanzania) | Collection and settlement only through a licensed provider; no unauthorised deposit-taking | PSP and counsel; REG-04 |
| Courier and postal services (TCRA) | Carriers must be licensed for the services used | Carrier due diligence; REG-05 |
| Tax (TRA) | VAT and corporate tax treatment, invoices and records | Accountant and counsel; REG-06 |
| Business registration (BRELA) | Company registration and filings | Company secretary; REG-07 |
| Fair competition and consumer protection | Honest pricing, no misleading claims, fair supplier terms | Counsel; REG-08 |
| Product safety and standards | Baby products, appliances, cosmetics, recalls | Category leads and counsel; REG-09 to REG-11 |
| Employment and contractor law | Rider and staff engagement model | Counsel; REG-12 |

The platform does not assert that it complies until counsel has confirmed the position and the controls are evidenced. Compliance is a launch gate, not a post-launch task.

---

# 12. Assumptions, constraints and dependencies

## 12.1 Business assumptions

| ID | Assumption | Test |
|---|---|---|
| A-01 | Customers will pay online through a PSP | Observe payment success and abandonment in first cohort |
| A-02 | Six departments can be supplied credibly by 40 suppliers | Supplier recruitment against department targets |
| A-03 | 40 suppliers can deliver 800–1,200 active SKUs | Catalogue audit at launch |
| A-04 | 900 orders in month 6 is achievable at planned acquisition cost | Monthly acquisition and conversion tracking |
| A-05 | 8% commission is acceptable to suppliers | Contract negotiation and churn |
| A-06 | TZS 5,000 delivery charge is viable with a minimum basket | Carrier quotes and basket data |
| A-07 | A 7-day return window is workable across categories | Return rate and dispute data |
| A-08 | Manual logistics can support launch volume | Shipments per operator per day |
| A-09 | Support volume is manageable with one agent | Tickets per 100 orders |
| A-10 | Suppliers will keep stock current | Weekly stock update rate |
| A-11 | Moderation can be staffed part-time | Queue age during onboarding |
| A-12 | Swahili-first is the right default | Language switching and support language mix |
| A-13 | A minimum basket will not destroy conversion | Checkout test |
| A-14 | 8–12 weeks is achievable with the stated team | Week-8 gate |

## 12.2 Constraints

- One city, one currency, one legal entity at launch.
- No platform-held customer funds.
- No hard-coded Usiri dependency; any carrier integration must be replaceable.
- No warehouse, fleet or inventory ownership.
- Small team; no 24/7 support at launch.
- Payment only through a licensed provider.
- Brand use only under a written licence.

## 12.3 Dependencies

| Dependency | Needed by | Owner | Risk if late |
|---|---|---|---|
| PSP contract and sandbox | Before payment build | Finance lead | Payment cannot be built or tested |
| Carrier agreement and rate card | Before checkout pricing is frozen | Operations lead | Delivery promise and pricing unknown |
| Counsel memo on consumer, data and payment model | Before launch | Founders | Compliance gate fails |
| Supplier recruitment to 30 verified | Before catalogue freeze | Founders | Catalogue too thin to launch |
| Photography and content capacity | Before launch | Operations | Listings late or poor |
| Hosting and domain | Before build environment | CTO | Build blocked |
| Brand assets and domain clearance | Before public launch | Founders | Launch delay or rebrand |

---

# 13. Business risks

The full register is RSK-01 to RSK-21 in the discovery report and the amendment. The business-critical risks are:

| Risk | Business consequence | Mitigation | Owner |
|---|---|---|---|
| Scope sprawl across six departments | Late launch and shallow catalogue | Six bounded departments; week-8 scope gate | Founders |
| Supplier recruitment shortfall | No credible assortment | Dedicated recruitment; department quotas; onboarding incentives | Founders |
| Delivery failure rate | Trust collapse and refunds | Carrier qualification; zones; second attempt; measured promise | Operations |
| Return rate in fashion | Margin erosion | Size guides; fit reason codes; supplier scorecards; reserve | Category lead |
| Counterfeit or expired beauty | Legal and trust damage | Authenticity evidence; audits; delisting | Category lead |
| Baby safety incident | Liability and reputational harm | Declarations; recall checks; insurance; counsel | Founders |
| Payment or settlement error | Supplier distrust and loss | Ledger; daily reconciliation; maker-checker | Finance |
| Regulatory finding | Trading interruption | Counsel before launch; PSP structure; filings | Founders |
| Key-person dependency | Delivery stall | Documentation; second contributor; code access | CTO |
| Cash exhaustion | Stop before evidence | Lean scope; monthly burn review; stop rules | Founders |

---

# 14. Governance, approvals and change control

## 14.1 Stage gates

| Gate | Question | Evidence required | Approver |
|---|---|---|---|
| G0 | Is the business worth building? | Concept, discovery, decisions | Founders |
| G1 | Are the requirements agreed? | BRD and SRS signed off; open decisions assigned | Founders |
| G2 | Is the design safe and buildable? | Architecture, data, API, security and UX approved | Founders and technical lead |
| G3 | Is it ready to test? | Test plan, environments, test data, acceptance criteria | Technical lead and operations |
| G4 | Is it ready to launch? | Compliance memo, supplier cohort, carrier, PSP, runbooks | Founders |
| G5 | Should it scale, pivot or stop? | Month-6 evidence pack | Founders |

## 14.2 Change control

1. A change to scope is written, with the reason, the cost, the schedule effect and the risk.
2. The product owner assesses the impact against the traceability matrix.
3. The founders approve or reject at the next review; urgent safety changes may be approved by the duty manager and ratified within 48 hours.
4. Approved changes update the BRD, SRS and traceability matrix in the same version cycle.
5. No change is implemented by direct edit to code without a requirement and a test.

## 14.3 Sign-off

This BRD is approved when the founders confirm: the objectives and targets, the six-department boundary, the operating model, the business rules status, and the assignment of open decisions D-13 to D-20. Until then it remains a draft and does not authorize build.

---

# 15. Open items and next step

The blocking decisions D-01 to D-04 are closed. Eight sub-decisions remain:

| ID | Question | Needed by |
|---|---|---|
| D-13 | Exact six-department tree | BRD sign-off |
| D-14 | Minimum basket or small-order fee | Checkout design freeze |
| D-15 | Category commission schedule | Supplier contracts |
| D-16 | Beauty authenticity evidence | Beauty go-live |
| D-17 | Baby safety declaration | Baby go-live |
| D-18 | Fashion return policy | Policy publication |
| D-19 | Launch supplier cohort | Recruitment plan |
| D-20 | Timeline fallback | Roadmap sign-off |

The SRS will convert this BRD into numbered, testable requirements. The architecture, data, API and UX packs follow. No implementation begins until G2 is passed.

---

# Appendix A. Glossary

| Term | Meaning |
|---|---|
| Parent order | The customer's single commercial order from one checkout |
| Supplier order | The part of a parent order fulfilled by one supplier; the settlement unit |
| Shipment | A parcel with a carrier, waybill and proof of delivery |
| Variant | A purchasable combination of options, such as size and colour, with its own SKU |
| GOV | Gross order value, the merchandise value of orders before deductions |
| Contribution | Revenue less commission costs, delivery costs, payment fees and expected returns |
| Mode A | Manual logistics coordination at pilot |
| Mode B | Integrated logistics through a carrier API |
| KYC | Know-your-supplier verification of identity, business and payout account |
| POD | Proof of delivery |
| PSP | Licensed payment service provider |

# Appendix B. Document map

| Document | Purpose | Status |
|---|---|---|
| UM-DISC-001 | Discovery baseline, evidence, rules, gaps | v0.2 |
| UM-DEC-001 | Decision log | v0.2 |
| UM-AMD-001 | Decision outcome and scope amendment | v1.0 |
| UM-BRD-001 | This document | v1.0 |
| UM-SRS-001 | Numbered software requirements | Next |
| Architecture pack | System, data, API and security design | After SRS |
| UX pack | Flows, wireframes, content and accessibility | After SRS |
| Test, DevOps, DR and roadmap | Delivery planning | After design |
