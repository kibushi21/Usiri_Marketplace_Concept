# 0. Document control and status

| Field | Value |
|---|---|
| Document | Requirements Discovery Report |
| Project | Usiri Marketplace (working name) |
| Document ID | UM-DISC-001 |
| Version | 0.2 |
| Status | **Draft for founder review. Decisions D-01 to D-04 recorded 30 October 2026. No implementation is authorized.** |
| Date | 30 October 2026 |
| Prepared for | The founding group |
| Prepared by | Project initiator, acting as business analyst and software architect |
| Classification | Confidential — internal discussion |
| Related documents | `Usiri_Marketplace_Project_Concept.md` v1.0; `Group_Meeting_Pack.md`; `Startup_Budget_and_Decision_Workbook.xlsx`; `01_Decision_Log.md` v0.2; `03_Decision_Outcome_and_Scope_Amendment.md` v1.0 |
| Next document | Business Requirements Document (BRD) and Software Requirements Specification (SRS), using the amended scope |

> **Status notice.** Usiri Group of Companies is a **potential** logistics and brand partner, not a confirmed partner. This report does not assume that Usiri has approved the project, has an API, has a rate card, or has agreed to any franchise or brand licence. No code has been written. No supplier, carrier, payment provider or customer has committed to anything.

> **Amendment notice — 30 October 2026.** The founders answered the four blocking decisions. **D-01 was answered differently from the recommendation in this report:** the first release is **general merchandise**, not the focused home-and-kitchen pilot. D-02, D-03 and D-04 were accepted as recommended. The consequences are issued separately as **UM-AMD-001, Decision Outcome and Scope Amendment**, which supersedes the scope statements in Section 3 and the DEC-01 entry in Section 14. Where this report and UM-AMD-001 differ on launch scope, UM-AMD-001 governs. The analysis in Sections 4 to 13 remains valid; the scope-dependent parts are restated in the amendment.

## 0.1 How evidence is labelled

| Label | Meaning |
|---|---|
| **[Confirmed]** | Stated in the project brief or agreed by the founders. It can be designed against. |
| **[Assumption]** | A planning assumption taken from the concept document. It must be tested before it becomes a requirement. |
| **[Proposed]** | A design recommendation in this report. It is not yet approved. |
| **[Open]** | A decision or fact that is unresolved. It is listed with an owner and an impact. |
| **[To verify]** | A claim, usually from a company or a secondary source, that has not been independently checked. |

---

# 1. Purpose, scope and method

## 1.1 Purpose

This report converts the proposed Usiri Marketplace concept into a structured discovery baseline: what the business is trying to achieve, who is involved, what the system must do at launch, which rules govern money and trust, what quality attributes matter, which legal obligations shape the design, and what remains unknown.

It is the input to the BRD and SRS. It is not the BRD, the SRS, the architecture document or the database design. Those documents come after the founders confirm the scope decisions in Section 14.

## 1.2 What this report is not

- It is not an approval to build, recruit, sign supplier agreements, approach payment providers as a merchant, or represent the project as a Usiri project.
- It is not a substitute for legal, tax, accounting or regulatory advice. Tanzanian counsel and a qualified accountant must review the positions marked **[Open]**.
- It is not a market study. The concept document already sets out the customer, supplier and carrier evidence still required.
- It is not a final technology selection. The brief proposes a stack; this report treats it as a strong default, not a commitment.

## 1.3 Inputs

1. **The project brief** supplied by the founders: a multi-vendor marketplace, a proposed franchise relationship with Usiri, provider-agnostic logistics, authorised payment providers, configurable branding, and a phased engineering process. **[Confirmed]**
2. **The concept document v1.0**, especially the business model (Section 4), journeys (Section 7), initial segment (Section 8), revenue model (Section 9), logistics (Section 10), technology direction (Section 11), legal map (Section 12) and MVP definition (Section 17). **[Confirmed as project intent]**
3. **Desk review of Tanzanian regulation** recorded in the concept document's source register. The sources are secondary summaries unless they are primary legislation or an official regulator page; they are cited in Appendix B and must be checked by counsel. **[To verify]**
4. **No primary field research has been completed**: no supplier interviews, customer interviews, carrier quotations, payment provider proposals or legal opinions are in hand. This is the largest evidence gap in the project and is treated as such throughout.

## 1.4 Method

The discovery followed six steps:

1. Decompose the brief into business objectives and scope boundaries.
2. Identify every actor, including actors who never log in but whose data or decisions enter the system.
3. Build a preliminary role and permission model from least privilege and separation of duties.
4. Map capabilities and the workflows that cross them, starting with the hardest case: one checkout spanning several suppliers.
5. Separate business rules, quality attributes and regulatory drivers so that they can be traced to requirements and tests later.
6. Record every unknown as a gap or an open decision, with an owner, a method and the impact of leaving it unresolved.

## 1.5 A note on precision

The report uses **must** for what the launch system is required to do, **should** for a strong expectation that may be traded against time, and **may** for an optional capability. These words are not decoration; they are the basis for acceptance testing in the SRS.

Where the concept document uses a planning number, such as an 8% commission or 900 orders in month six, this report labels it an assumption. A planning number is not a requirement. The system must make the number configurable; it must not hard-code it.

---

# 2. Business objectives and value proposition

## 2.1 The proposition in one paragraph

The marketplace lets a customer in Dar es Salaam buy everyday home, kitchen and small electrical goods from several verified shops in one checkout, pay through a licensed provider, receive a tracked delivery, and get a refund or replacement when something goes wrong. The platform earns a commission on completed sales, a supplier subscription and a delivery coordination fee; it does not buy stock, own vehicles or hold customer funds. **[Confirmed direction, Assumption on segment]**

## 2.2 Business objectives

| ID | Objective | Why it matters | How the pilot knows | Link to concept |
|---|---|---|---|---|
| OBJ-01 | Prove that customers will buy from several verified suppliers through one checkout | Demand is the first risk; without orders nothing else can be tested | 900 completed orders in pilot month 6 | Section 3.4 |
| OBJ-02 | Deliver reliably enough that customers trust the platform with repeat purchases | A late or lost parcel destroys trust faster than price attracts it | At least 90% on-time delivery; first-attempt success at least 80% | Section 10.8 |
| OBJ-03 | Resolve failures fairly and quickly | The first exception is the moment of truth | 90% of complaints resolved within 48 hours; returns below 5% | Section 7.4 |
| OBJ-04 | Recruit and retain credible suppliers | Supply quality determines catalogue quality and returns | 40 verified suppliers by month 3; 80% retention after 90 days | Section 8.5 |
| OBJ-05 | Prove positive contribution economics | Growth on negative unit economics destroys the company faster | Contribution at least 4% of gross order value by month 6 | Section 9 |
| OBJ-06 | Operate within Tanzanian law and the platform's contracts | A compliance failure can stop trading and damage the brand | Written legal baseline; registrations and filings completed as advised | Section 12 |
| OBJ-07 | Run the pilot with a small team without operational chaos | The team, not the software, is the constraint at launch | Every pilot order handled through the system; no shadow spreadsheets for money | Section 17.1 |
| OBJ-08 | Produce evidence for a scale, pivot or stop decision | The pilot exists to buy information, not to prove a point | Documented go/no-go review at month 6 | Section 19 |

## 2.3 Value by participant

| Participant | Value if the model works | What they give up or risk |
|---|---|---|
| Customer | One place to find verified household goods, transparent total price, tracked delivery, a remedy when something fails | A delivery fee, sharing an address and phone number, waiting for delivery instead of buying in person |
| Supplier | Demand, photography and catalogue help, delivery coordination, a payment process, and a customer-service buffer | Commission, service standards, stock accuracy, packing work, return exposure when at fault |
| Carrier | Predictable parcel volume, consolidated pickups or drop-offs, digital manifests and labels | Service-level commitments, tracking discipline, liability for loss and damage under its terms |
| Payment provider | Transaction volume and merchant fees | Must satisfy its own onboarding, risk and settlement rules; the platform cannot ask it to bend licensing rules |
| Franchise or brand partner | Brand reach and a new channel without building the technology | Reputational exposure if service fails; brand standards must be enforceable |
| Founders | A chance to build a defensible operating business with modest fixed assets | Time, reputational capital, legal exposure, and the risk that the market does not respond |

## 2.4 Revenue lines and the rule that protects them

The concept proposes four revenue lines: commission on completed sales, supplier subscriptions, a delivery coordination fee, and sponsored placement later. **[Assumption]**

Three rules follow for the software:

1. **Pass-through money is not revenue.** Carrier charges, supplier goods value and refunded amounts must be recorded separately from commission, subscription and coordination revenue.
2. **Commission follows completion, not capture.** Commission is earned on net merchandise value after discounts and returns, not on the amount first collected.
3. **Every revenue line is configurable and effective-dated.** A rate change must not silently rewrite historical orders.

## 2.5 What must be true

The concept document names six conditions: customers pay for reliability, suppliers accept the commission and rules, delivery can be bought at a predictable rate, returns stay below 5%, fixed costs stay lean, and ancillary revenue is real. **[Assumption]** If the first four fail together, the business model does not work, and no amount of software fixes it. The discovery process therefore treats supplier and customer willingness as **blocking evidence**, not as background research.

---

# 3. Scope boundary

> **Superseded in part — see UM-AMD-001.** Sections 3.1 and 3.2 below record the scope recommendation made before the founders decided. The **decided** launch scope is general merchandise, bounded to six departments: homeware, storage and kitchenware; small kitchen and home appliances; fashion and footwear; beauty and personal care; baby and maternity; and home and kitchen bundles. Forty verified suppliers and 800–1,200 SKUs at launch, rising to 60 suppliers by month six. Section 3.3 (operating constraints) and Section 3.4 (scope change rule) remain in force. The full amended scope, category price bands, variant requirements and the added rules, gaps and risks are in UM-AMD-001.

## 3.1 In scope for the first release

The first release is the smallest system that lets a real customer buy from several real suppliers, pay by mobile money or card through a licensed provider, receive a tracked delivery, and obtain a refund. It includes:

- A mobile-first customer web application (responsive site or PWA) in Swahili and English.
- Guest checkout and optional customer accounts.
- A supplier portal for onboarding, catalogue, stock, orders, dispatch and statements.
- An operations and administration console for verification, moderation, orders, payments, payouts, logistics, returns, support and reporting.
- A logistics coordination module that works manually at pilot and is provider-agnostic.
- Payment integration through an authorised payment service provider (PSP), with reconciliation and refunds.
- A support and dispute workflow with order context.
- Audit logging, role-based access control and the legal pages needed at checkout.

## 3.2 Explicitly out of scope for the first release

| Excluded | Reason | Revisit when |
|---|---|---|
| Native iOS and Android applications | Web/PWA reaches more people at lower cost; app reviews add delay | Repeat purchase and traffic justify the cost |
| Marketplace-owned warehouse or dark store | Contradicts the asset-light model and adds fixed cost | Supplier density or delivery density makes consolidation economic |
| Marketplace-owned fleet | Capital and operational burden; carriers are licensed for this | Volume and route density justify it, if ever |
| Real-time GPS tracking | Carrier capability unknown; status events are enough for the promise | A carrier offers reliable event data and customers demand it |
| Customer wallet, credit or instalments | Licensing, fraud and float risk | Licensed partner and proven fraud controls |
| Buyer-seller chat | Disintermediation, abuse and moderation cost | Never in the current model |
| Multi-city operations | Operations must be proven in one city first | Expansion criteria in concept Section 8.6 are met for two consecutive months |
| International shipping and multi-currency | Customs, tax and delivery complexity | After domestic model is profitable |
| AI recommendations and personalisation | No behavioural data; adds cost and privacy surface | Catalogue and traffic are large enough to matter |
| Automated supplier payouts | Manual approval is safer while volumes are low | Reconciliation is stable and payout volume justifies automation |
| Microservices and event streaming | Complexity without measured need | A measured bottleneck cannot be solved inside the monolith |
| Advertising auction and loyalty programme | No traffic or repeat base yet | After 12 months of stable operations, if ever |

## 3.3 Operating constraints

- **One city, one currency.** Dar es Salaam; Tanzanian shillings. **[Assumption]**
- **One legal entity owns the platform and its contracts.** The founders establish the operating company. **[Confirmed]**
- **No platform-held customer funds.** Payment collection and settlement run through an authorised provider; the platform does not operate an informal escrow or deposit scheme. **[Confirmed]**
- **No Usiri dependency in the critical path.** The system must work with any qualified carrier and must not contain a hard-coded Usiri integration. **[Confirmed]**
- **Brand and franchise rules are configuration, not code.** Territory, fee display, brand assets and approval rules must be data-driven. **[Confirmed]**
- **Small team.** The pilot assumes one technical lead, one developer, a part-time designer and an operations lead. **[Assumption]**

## 3.4 Scope change rule

A capability enters the first release only if it is required to complete, deliver, refund or support a pilot order, or to meet a legal obligation. Everything else is deferred, however attractive. This rule is deliberately strict because the most common MVP failure is not a missing feature; it is a system the team cannot operate.

---

# 4. Stakeholder analysis

## 4.1 Stakeholder register

| ID | Stakeholder | Primary interest | Responsibility | Interaction with the system | Influence / interest |
|---|---|---|---|---|---|
| STK-01 | Guest visitor | Browse without committing; understand price and delivery before registering | None beyond lawful use | Catalogue, search, cart, guest checkout | Low influence, high interest |
| STK-02 | Registered customer | Buy reliably, track orders, return items, get help | Keep contact and address accurate; pay; collect parcel | Account, orders, returns, reviews, tickets | Medium influence, high interest |
| STK-03 | Individual merchant | Sell more without hiring a delivery desk | List accurately, keep stock current, pack to standard | Supplier portal, orders, statements | Medium influence, high interest |
| STK-04 | Business supplier | A predictable channel that protects its reputation | Contract, compliance, product quality, fulfilment | Supplier portal plus commercial reporting | High influence on supply, high interest |
| STK-05 | Supplier employee | Clear daily tasks without exposure to sensitive data | Pack, dispatch, respond to order alerts | Limited supplier sub-account | Low influence, medium interest |
| STK-06 | Logistics provider | Profitable, predictable parcel volume | Pickup, line-haul, delivery, status events, claims | Carrier portal or manual coordination; adapter later | High influence on delivery promise |
| STK-07 | Logistics agent or driver | Clear stops and proof of delivery | Collect and deliver; record status and POD | Mobile-friendly status page or carrier app | Low influence, high interest |
| STK-08 | Customer support agent | Resolve issues quickly with full context | Triage, communicate, escalate, document | Support console, order context, refunds requests | High influence on trust |
| STK-09 | Finance personnel | Accurate money, timely payouts, clean reconciliation | Reconcile, approve payouts, process refunds, report | Payments, ledger, settlements, reports | High influence, high interest |
| STK-10 | Catalogue moderator | A trustworthy, accurate catalogue | Review listings, categories, images, claims | Moderation queue, product records | Medium influence |
| STK-11 | Operations administrator | Orders move and exceptions close | Book carriers, monitor dispatch, resolve exceptions | Operations console, shipment records | High influence on service |
| STK-12 | Super administrator | The platform is controlled and auditable | Manage staff, roles, configuration, sensitive approvals | Full administration, audit logs | High influence |
| STK-13 | Franchise or brand manager | Brand standards and licence compliance | Approve brand use, review reports, audit standards | Brand configuration, compliance reports | High influence if a licence exists; currently none |
| STK-14 | Technology administrator | A secure, available system | Deploy, monitor, patch, restore | Infrastructure, logs, configuration | High influence, low business-data interest |
| STK-15 | Auditor or adviser | Evidence that controls work | Review records, test controls, report | Read-only audit and financial views | Low influence, high interest |
| STK-16 | Regulators and authorities | Compliance with applicable law | Investigate, license, enforce, advise | Legal requests outside normal product access | High influence, episodic |

## 4.2 External systems as dependencies

| Dependency | What the platform needs | What is confirmed | Risk if unavailable |
|---|---|---|---|
| Payment service provider | Merchant onboarding, collection, refunds, settlement reports, webhooks, reconciliation file | Nothing | No way to take payment lawfully at scale |
| Carrier | Rate card, booking, waybill, tracking events, POD, claims, liability terms | Nothing; Usiri publishes no API or rate card | Delivery promise cannot be costed or tracked |
| SMS gateway | Sender ID, delivery receipts, OTP delivery | Nothing | Customers cannot verify or receive updates |
| WhatsApp Business provider | Template approval, message delivery | Nothing | Reduced communication channel, not fatal |
| Object storage and CDN | Image and document storage, signed URLs | Vendor selection open | Catalogue and KYC documents cannot be stored safely |
| Hosting and database | Managed runtime, backups, private networking | Vendor selection open | No production environment |
| Identity or KYC service | Document checks and liveness, where used | Nothing | Manual verification remains the fallback |
| Accounting or ERP | Export of sales, commission, payouts and tax lines | Nothing | Manual journal preparation; error risk |
| Email provider | Transactional email and support | Nothing | Minor, SMS remains primary |

## 4.3 Governance and decision rights (preliminary)

| Decision | Proposed authority | Consultation | Notes |
|---|---|---|---|
| Product scope and MVP trade-offs | CEO or product owner | CTO, operations lead | Documented in the decision log |
| Architecture and security standards | CTO or technical lead | CEO, external reviewer for high-risk changes | No production change without review |
| Supplier approval or suspension | Operations lead | Finance if money is at risk | Suspension is a sensitive action requiring a reason |
| Refund above threshold | Finance lead | CEO above a higher threshold | Thresholds to be set before pilot |
| Supplier payout batch | Finance preparer plus second approver | CEO for exceptions | Maker-checker is mandatory |
| Brand or franchise commitments | Founders unanimously | Legal counsel | No individual may sign alone |
| Data access for staff | Super administrator | CTO | Time-bound, logged, reason required |
| Regulatory filings | Finance and compliance owner | Counsel | Calendar with evidence of submission |

---

# 5. Preliminary role and access model

## 5.1 Principles

1. **Deny by default.** A role receives only the permissions explicitly granted to it.
2. **Least privilege.** Access is limited to the data and actions needed for the task, not to the department.
3. **Separation of duties.** The person who prepares a payout cannot be the only person who approves it.
4. **Field-level protection.** A supplier sees the delivery name, phone and address needed to pack and hand over, but not the customer's order history, payment details or other suppliers' data.
5. **Scoped queries.** Every supplier, carrier and customer query is filtered by tenant ownership at the data-access layer, not only in the interface.
6. **Audit everything sensitive.** Role changes, refunds, payouts, price overrides, supplier suspension and data exports are recorded with actor, time, reason and before/after values.
7. **No shared accounts.** Staff accounts are individual; break-glass access is time-bound and reviewed.

## 5.2 Role catalogue

| ID | Role | Scope |
|---|---|---|
| ROL-01 | Guest | Unauthenticated visitor with a temporary cart |
| ROL-02 | Customer | Registered buyer acting on their own account |
| ROL-03 | Supplier owner | Legal owner or authorised manager of one supplier account |
| ROL-04 | Supplier staff | Employee of one supplier with task-level permissions |
| ROL-05 | Logistics provider administrator | Administrator of one carrier organisation |
| ROL-06 | Logistics agent or driver | Field user assigned to specific shipments or stops |
| ROL-07 | Support agent | Customer-service staff with order and ticket access |
| ROL-08 | Finance personnel | Staff responsible for payments, refunds, reconciliation and payouts |
| ROL-09 | Catalogue moderator | Staff responsible for product and category quality |
| ROL-10 | Operations administrator | Staff responsible for order and shipment operations |
| ROL-11 | Super administrator | Platform owner role for configuration and sensitive approvals |
| ROL-12 | Franchise or brand manager | Brand-licence representative with compliance visibility only |
| ROL-13 | Technology administrator | Infrastructure and deployment role without default business-data access |
| ROL-14 | Auditor | Read-only review role for controls and records |

## 5.3 Permission matrix

The matrix states the **maximum** permission of the role. A specific user may be granted less, never more, without a super-administrator decision and an audit record.

::: {.rbac-table}
| Role | View | Create | Edit | Approve | Delete | Explicitly cannot |
|---|---|---|---|---|---|---|
| ROL-01 Guest | Published catalogue, storefronts, policies, delivery estimate | Cart session, guest checkout, support enquiry | Own cart only | Nothing | Own cart items | View any placed order, customer record, supplier record, payment data or internal note |
| ROL-02 Customer | Own profile, addresses, orders, returns, tickets, own reviews | Order, return request, ticket, review, saved address | Own profile and address before dispatch; own review within edit window | Nothing | Own saved address or wishlist item | See another customer, supplier cost or margin, internal notes, or staff data |
| ROL-03 Supplier owner | Own store, products, stock, own supplier orders and fulfilment fields, own statements, own scorecard | Product, variant, price, stock update, dispatch request, promotion request, staff invitation | Own catalogue, stock, store profile, order preparation fields | Nothing financial or platform-wide | Archive own product; remove own draft | See other suppliers, full customer profiles, commission configuration, platform reports, another store's payouts |
| ROL-04 Supplier staff | Assigned store products and orders needed for packing | Draft product, stock adjustment, dispatch status | Stock, order preparation, own profile | Nothing | Nothing | See payout account, contract, commission rate, customer history, other suppliers, staff roles |
| ROL-05 Logistics provider administrator | Assigned shipments, own service areas and rates, own performance report | Shipment acceptance, status event, claim, service area proposal | Own shipment status and POD, own profile | Nothing commercial | Nothing in production | See order prices, commissions, customer payment data, other carriers, platform margin |
| ROL-06 Logistics agent or driver | Assigned stops and recipient contact needed to deliver | Status event, POD, failed-attempt reason | Assigned delivery data only | Nothing | Nothing | Browse all orders, see order value, customer history or payment information |
| ROL-07 Support agent | Customer and order context, tickets, returns, masked payment status | Ticket, return request, refund request, internal note | Ticket status and notes, contact details with reason | Nothing financial | Nothing | Approve refunds or payouts, change commission, export full customer database, view full card data |
| ROL-08 Finance | Payments, ledger, refunds, payouts, reconciliation, financial reports | Payout batch, refund record, journal adjustment request | Draft financial records before approval | Refund and payout within delegated limit | Nothing | Edit catalogue, change supplier KYC except finance fields, alter audit logs, approve own adjustment |
| ROL-09 Catalogue moderator | Products, categories, brands, moderation queue, supplier quality flags | Category, brand, moderation note | Listing metadata and moderation status | Approve or reject listing | Archive listing only | See customer PII, payments, payouts, supplier bank details |
| ROL-10 Operations administrator | Orders, shipments, supplier operations, exceptions, carrier performance | Carrier booking, shipment record, supplier task, exception case | Order operations fields, carrier assignment, promised date with reason | Nothing financial | Nothing | Approve payouts, change commission, view full KYC unless operationally required |
| ROL-11 Super administrator | All business data and configuration, audit logs | Staff account, role, configuration, promotion, category | Any business record subject to change control | Sensitive actions with a second approver | Soft-delete or archive only | Delete audit logs, approve own financial adjustment alone, access production secrets without break-glass |
| ROL-12 Franchise or brand manager | Brand assets, brand compliance reports, aggregate commercial reports | Brand content within licence scope | Brand settings within licence scope | Brand usage approval | Nothing | See customer PII, supplier contracts, individual orders, payout amounts |
| ROL-13 Technology administrator | Infrastructure, deployment status, logs, configuration, error traces | Service account, environment, deployment | System configuration through change process | Deploy through change approval | Nothing business-critical | Read customer PII or financial records without break-glass approval; alter audit records |
| ROL-14 Auditor | Audit logs, financial records, policies, control evidence | Nothing | Nothing | Nothing | Nothing | Edit any record; view unmasked customer PII beyond what the audit purpose requires |
:::

## 5.4 Sensitive data classes

| Class | Examples | Default handling | Roles with access |
|---|---|---|---|
| Identity and KYC | National ID, business registration, TIN, beneficial owner, site-visit evidence | Encrypted at rest; private object storage; signed URLs; access logged | Supplier owner for own documents; ROL-08, ROL-11, ROL-14; ROL-10 only when required |
| Contact and address | Name, phone, delivery address, landmark, alternate recipient | Masked in lists; revealed to assigned supplier and carrier only for fulfilment | ROL-02 for own data; ROL-03 and ROL-05 for assigned orders; ROL-07 with reason; ROL-08 where needed |
| Order and commercial | Items, prices, discounts, commission, delivery cost, margin | Supplier sees own order lines and its commission, not platform-wide margin | ROL-02 own orders; ROL-03 own orders; ROL-07, ROL-08, ROL-10, ROL-11 |
| Payment | PSP reference, amount, status, refunds, settlement | No card data stored; PSP token or reference only | ROL-08, ROL-11, ROL-14 masked; customer sees own status |
| Credentials and secrets | Password hashes, API keys, webhook secrets | Managed secret store; never in source or logs | ROL-13 through controlled process only |
| Audit and security | Login history, admin actions, access reasons | Append-only; restricted read | ROL-14, ROL-11, ROL-13 for security events |

## 5.5 Segregation of duties

| Activity | Preparer | Approver | Rule |
|---|---|---|---|
| Supplier payout | Finance | Second finance user or CEO | Same person cannot prepare and approve |
| Refund above threshold | Support or finance | Finance lead | Threshold set before pilot; above it, CEO |
| Supplier suspension | Operations | Super administrator | Written reason and evidence |
| Commission or fee change | Finance or CEO | Founders or delegated owner | Effective date required; no retroactive change without approval |
| Role or permission change | Super administrator | Second founder | Logged with before/after |
| Production data access | Technology administrator | Super administrator break-glass approval | Time-bound; session recorded |
| Brand or franchise commitment | Founders | Unanimous founders plus counsel | No unilateral signature |

## 5.6 Authentication requirements (draft)

- Customers authenticate by phone number with a one-time code; email and password may be offered as an alternative. **[Proposed]**
- Staff and suppliers require a password plus multi-factor authentication. **[Proposed]**
- Supplier staff accounts are invited by the supplier owner and can be revoked immediately. **[Proposed]**
- Sessions expire after inactivity; sensitive actions require re-authentication. **[Proposed]**
- Login, OTP and password-reset attempts are rate-limited and monitored. **[Proposed]**
- All authentication events are logged without recording secrets or full OTP values. **[Proposed]**

## 5.7 Open access questions

| ID | Question | Impact |
|---|---|---|
| O-RBAC-01 | Will suppliers be allowed to create sub-users at launch, or only after pilot? | Affects supplier onboarding and support load |
| O-RBAC-02 | Should support agents see full customer phone numbers or a masked value with a reveal action? | Balances service speed against data minimisation |
| O-RBAC-03 | Does the franchise or brand partner need any access to individual orders, or only aggregate compliance reports? | Affects tenant model and data-sharing agreement |
| O-RBAC-04 | Is a separate auditor account required by any investor, lender or regulator? | Affects evidence export and access review |
| O-RBAC-05 | What is the refund approval threshold for finance and for the CEO? | Needed before pilot, not before build |

---

# 6. Capability map and module inventory

## 6.1 Capability map

Priority: **Must** means required for the pilot; **Should** means planned shortly after launch; **Later** means explicitly deferred.

::: {.cap-table}
| ID | Capability | What it must cover | Priority and dependencies |
|---|---|---|---|
| CAP-01 | Identity, authentication and consent | Customer, supplier and staff accounts; phone verification; MFA for staff; sessions; consent records; role assignment | Must. Foundation for every other capability |
| CAP-02 | Supplier onboarding and KYC | Application, document upload, verification workflow, site visit, contract record, approval, suspension, re-verification | Must. Depends on CAP-01 and document storage |
| CAP-03 | Catalogue and moderation | Products, variants, categories, attributes, brands, images, pricing, approval, visibility, prohibited-item checks | Must. Depends on CAP-02 |
| CAP-04 | Inventory and availability | Stock per variant, reservation, release, low-stock alerts, suppression at zero, supplier stock updates | Must. Depends on CAP-03 |
| CAP-05 | Search, browse and discovery | Keyword search, category browse, filters, sort, related products, zero-result handling | Must. Depends on CAP-03 |
| CAP-06 | Cart and checkout | Multi-supplier cart, price and stock validation, address, delivery quote, fees, payment selection, order submission | Must. Depends on CAP-04, CAP-05, CAP-10 |
| CAP-07 | Orders and fulfilment orchestration | Parent order, supplier sub-orders, items, statuses, cancellations, partial fulfilment, event history | Must. Depends on CAP-06 |
| CAP-08 | Payments and reconciliation | Payment initiation, callback verification, idempotency, ledger, refunds, reconciliation, mismatch handling | Must. Depends on CAP-07 and a PSP agreement |
| CAP-09 | Settlements and supplier payouts | Commission calculation, statements, holds, payout batches, dual approval, adjustments, export | Must. Depends on CAP-08 |
| CAP-10 | Logistics and tracking | Provider register, service areas, rates, shipment records, labels, booking, status events, POD, exceptions, claims | Must, with manual mode. API adapter later |
| CAP-11 | Returns, refunds and disputes | Return request, eligibility, evidence, approval, reverse logistics, inspection, refund calculation, supplier chargeback, dispute | Must. Depends on CAP-07, CAP-08, CAP-10 |
| CAP-12 | Customer support | Ticket queue, order context, assignment, internal notes, escalation, SLA timers, resolution | Must. Depends on CAP-07 |
| CAP-13 | Notifications | SMS, WhatsApp and email templates; event triggers; delivery status; failure handling; consent-aware marketing | Must. Depends on CAP-01, CAP-07 |
| CAP-14 | Administration and governance | Staff, roles, permissions, configuration, approvals, audit logs, data export, feature flags | Must. Depends on CAP-01 |
| CAP-15 | Reporting and analytics | Orders, GMV, revenue, contribution, returns, delivery performance, supplier scorecards, cohort retention | Must for basic reports; Should for cohorts |
| CAP-16 | Reviews and ratings | Verified-buyer reviews, moderation, supplier reply, abuse reporting | Should. Depends on CAP-07 |
| CAP-17 | Promotions and sponsored placement | Vouchers, supplier-funded discounts, campaign tracking, sponsored slots | Should for vouchers; Later for auction |
| CAP-18 | Franchise and brand configuration | Brand assets, territory rules, fee display, approval workflow, compliance reports | Must if a licence is signed; otherwise configurable but inactive |
:::

## 6.2 Dependency order

The build order is constrained by data dependencies, not by screen count:

1. Identity, roles, consent and audit (CAP-01, CAP-14).
2. Supplier onboarding and catalogue (CAP-02, CAP-03, CAP-04).
3. Customer discovery, cart and checkout (CAP-05, CAP-06).
4. Orders, payments and ledger (CAP-07, CAP-08).
5. Logistics and fulfilment (CAP-10).
6. Returns, support and settlements (CAP-11, CAP-12, CAP-09).
7. Reporting, reviews and promotions (CAP-15, CAP-16, CAP-17).

A team that builds checkout before supplier verification and stock reservation will create orders the platform cannot fulfil. A team that builds payments before the order and ledger model will create reconciliation debt from the first transaction.

## 6.3 Requirements status convention

Every capability will be decomposed in the SRS into requirements with an ID, a statement, a priority, a source and an acceptance criterion. The discovery baseline does not yet assign thousands of low-level requirements. It establishes the modules, rules and quality attributes that those requirements must respect.

---

# 7. Critical end-to-end workflows

## 7.1 WF-01: Customer purchase across several suppliers

**Actors:** guest or customer, marketplace, PSP, supplier sub-orders, carrier.

1. Customer browses or searches; results show price, stock status, seller and delivery promise.
2. Customer adds items from one or more suppliers to a single cart.
3. At cart and checkout, the platform revalidates price and stock server-side. It does not trust the browser.
4. Customer enters a phone number and delivery address, including a landmark. The platform validates the zone and shows the delivery fee and total before payment.
5. The platform creates a payment intent with a unique idempotency key and a reference that can be reconciled.
6. The customer pays through the PSP. The platform never treats the browser's success message as proof of payment.
7. On a verified callback or server-side status query, the platform creates the parent order and supplier sub-orders, reserves stock, and records the payment.
8. The customer sees one order number and one support thread. Each supplier sees only its sub-order and the fulfilment data it needs.
9. Notifications confirm the order and set expectations for split deliveries.
10. If payment fails, stock is released, the cart remains recoverable and no order is created. If stock is lost between checkout and payment confirmation, the affected line is cancelled and refunded before the rest proceeds.

**Failure paths that must be designed:** duplicate submission, delayed callback, callback received before the order record is committed, payment succeeded but stock reservation failed, address outside the zone, one supplier rejecting while others accept, and a customer closing the browser after paying.

## 7.2 WF-02: Supplier fulfilment

1. Supplier receives an order alert by SMS, WhatsApp, email or dashboard, according to preference.
2. Supplier accepts or rejects within a stated window. Rejection requires a reason code and releases the line for refund.
3. On acceptance, the supplier prepares the parcel to the packaging standard, prints the packing slip and label, and marks it ready for handover.
4. Operations or the carrier records the handover: time, parcel count, weight, condition and waybill.
5. The shipment moves through carrier status events until delivery or a failed attempt.
6. The supplier sees its own service metrics: acceptance rate, on-time handover, cancellation rate, return rate and unresolved complaints.

**Control:** the platform must not allow a supplier to mark an order delivered. Delivery is a carrier or operations event with evidence. The supplier can mark ready for handover, not delivered.

## 7.3 WF-03: Payment verification and reconciliation

1. The platform creates a payment intent with amount, currency, order reference, customer reference and idempotency key.
2. The PSP returns a redirect or push prompt. The customer completes payment in the PSP channel.
3. The PSP sends a callback. The platform verifies the signature, timestamp and reference, then retrieves the authoritative status from the PSP server-to-server.
4. The platform writes a payment record and double-entry ledger entries. It updates the order only after the authoritative status is `paid`.
5. A scheduled reconciliation job compares the platform ledger with the PSP settlement report by reference and amount.
6. Mismatches enter an exception queue with an owner. They are never silently adjusted.
7. Refunds are initiated against the original payment, recorded separately, and reconciled on the same schedule.

**Rules:** idempotency on initiation and callback; no client-side trust; no card data stored; every money movement has a reference; reconciliation exceptions are visible to finance; failed or reversed payments release stock and notify the customer.

## 7.4 WF-04: Manual logistics at pilot (Mode A)

The carrier may have no API, no rate card and no working tracking page. The pilot therefore runs a manual process through the operations console while recording every step as structured data.

1. Operations selects a carrier and service for the parcel, using a maintained rate card or a written quotation.
2. Operations records the quote, books the shipment by phone, email or carrier portal, and enters the booking reference.
3. The platform generates a label and manifest with order, sub-order, parcel and supplier references.
4. At handover, operations records time, weight, dimensions, condition and a photograph.
5. Operations updates shipment status from a daily status file or a phone call. Every update records source and timestamp.
6. On delivery, operations attaches proof of delivery: photo, signature, code or carrier confirmation.
7. Exceptions use a controlled reason code list: address, unavailable, refused, damaged, lost, carrier delay, supplier delay.
8. Claims and carrier invoices are matched to shipment records.

**Design requirement:** manual coordination is a first-class provider implementation, not a temporary hack. The same shipment record and event history must be used when an API carrier is added.

## 7.5 WF-05: Integrated logistics (Mode B)

A carrier adapter exposes a common capability set: quote, book, cancel, label, track, proof of delivery and claim. The platform asks the provider which capabilities it supports and degrades gracefully when one is missing.

- **Quote:** request by origin, destination, weight, dimensions and declared value; response includes price, currency, transit time and expiry.
- **Book:** idempotent request with the platform shipment reference; response includes waybill and label.
- **Track:** webhook where available, polling where not; events are normalised into platform status codes.
- **Proof of delivery:** document or code attached to the shipment, with timestamp and recipient evidence.
- **Claim:** structured loss or damage claim linked to shipment, evidence and carrier response.

**Rule:** no carrier-specific field may leak into the core order model. Provider-specific payloads are stored as adapter metadata, not as columns that every other module must understand.

## 7.6 WF-06: Returns, refunds and disputes

1. Customer requests a return within the published window, selecting a reason and uploading evidence where required.
2. The platform checks eligibility: delivered date, item category, condition, prior returns and whether the item is excluded.
3. Support or an automated rule approves, rejects or requests more evidence. High-value or disputed cases escalate.
4. If approved, the platform books reverse logistics or instructs a drop-off, and records the return shipment.
5. The supplier or operations inspects the item and records the outcome: resellable, damaged, missing parts, not the ordered item.
6. The refund is calculated from the item value and the applicable delivery share, less any lawful deductions. It cannot exceed the captured amount minus earlier refunds.
7. Finance approves according to threshold, the PSP processes the refund, and the customer is notified at each step.
8. If the cause is the supplier's, the amount is charged back against the supplier's payable, with evidence. If the carrier is responsible, a carrier claim is opened. If the platform is responsible, the platform bears the cost.
9. A dispute remains open until the customer is informed of the outcome and the money movement is complete.

**Key rule:** a return is not complete when the item is collected; it is complete when inspection, refund and communication are all closed.

## 7.7 WF-07: Supplier onboarding and KYC

1. Supplier applies with business name, owner identity, TIN, business registration, shop address, contact and category.
2. Supplier uploads documents and accepts the platform agreement, commission terms and service standards.
3. Operations verifies documents, performs a site visit where required, and records evidence.
4. Finance verifies the payout account name against the business identity.
5. The supplier is approved, rejected with reasons, or approved with conditions. Approval creates the store and supplier owner account.
6. Supplier uploads products, which enter moderation before publication.
7. A probation period applies: higher monitoring, lower payout frequency or a hold, according to policy.
8. Re-verification is scheduled periodically and after a material change of ownership, bank account or category.

**Data protection:** KYC documents are sensitive personal and business data. Access is logged, retention is defined by legal advice, and documents are never placed in a public bucket.

## 7.8 WF-08: Support and escalation

1. Customer contacts support by phone, WhatsApp, email or a form linked to an order.
2. A ticket is created with order context, category, priority and promised response time.
3. The agent diagnoses using order, payment, shipment and supplier information, without exposing internal notes to the customer.
4. Simple issues are resolved directly. Refunds, supplier penalties and carrier claims follow approval rules.
5. Multi-party disputes link the customer, supplier and carrier records, with evidence and a timeline.
6. Escalation triggers on age, value, repeat contact or a safety issue.
7. Closure requires a resolution code, customer communication and any financial action completed.
8. Repeat causes feed the supplier scorecard and the operations improvement log.

---

# 8. Order structure and state model

## 8.1 Recommended order structure

The marketplace should model five related records, not one flat order:

| Record | Purpose | Key fields |
|---|---|---|
| **Order** (parent) | The customer's commercial unit: one checkout, one payment relationship, one support thread, one visible order number | Customer, address snapshot, currency, totals, payment status, aggregate status, policy versions, channel |
| **Supplier order** (sub-order) | The fulfilment and settlement unit for one supplier | Supplier, items, merchandise subtotal, discount share, commission, delivery share, status, promised dates, cancellation reason |
| **Order item** | The priced line, with a snapshot of product and variant at purchase time | Product and variant references, title and SKU snapshot, quantity, unit price, discount, tax line, commission, return status |
| **Shipment** | The physical parcel unit | Carrier, service, waybill, parcel count, weight, dimensions, cost, status, POD, exception reason |
| **Financial entry** | The money movement and allocation | Payment, refund, commission, coordination fee, carrier payable, supplier payable, tax, ledger accounts |

**Recommendation [Proposed]:** one checkout creates one parent order and one supplier order per supplier. A supplier order may have one or more shipments; a shipment may contain items from only one supplier. The customer sees the parent order; the platform operates the supplier orders and shipments.

## 8.2 Why this structure

- **Customer experience:** one order number and one support conversation, even when three parcels arrive on different days.
- **Supplier isolation:** each supplier sees only its own sub-order and the customer data needed to fulfil it.
- **Financial correctness:** commission, refunds and payouts are calculated per supplier order, which is the only level at which liability and settlement make sense.
- **Operational reality:** parcels, carriers and proof of delivery belong to shipments, not to the parent order.
- **Partial failure:** one supplier can reject or cancel without corrupting the other suppliers' orders or the customer's payment record.

A single order per supplier would force the customer to pay several times and would break the promise of one checkout. A single global status would be unable to express "two parcels delivered, one still in transit". Both alternatives create support and accounting debt.

## 8.3 Separate state dimensions

A single status enum cannot represent payment, fulfilment, return and dispute at the same time. The system should keep separate, auditable state dimensions and derive the customer-facing summary. **[Proposed]**

| Dimension | Example values |
|---|---|
| Payment status | pending, authorised, paid, failed, partially refunded, refunded, reversed |
| Supplier order status | awaiting acceptance, accepted, preparing, ready for handover, in transit, delivered, completed, cancelled, return in progress, returned |
| Shipment status | pending, booked, picked up, in transit, at hub, out for delivery, delivered, failed attempt, returned to sender, lost, damaged |
| Return status | requested, approved, rejected, in transit back, received, inspected, refund pending, refunded, closed |
| Dispute status | open, investigating, awaiting evidence, resolved, escalated, closed |

The customer-facing summary is a projection: for example, "Partially delivered" when one supplier order is delivered and another is in transit. It is computed, not manually set.

## 8.4 Transition authority

| From | To | Who may trigger | Guard |
|---|---|---|---|
| Payment pending | Paid | System after verified PSP status | Signature valid; amount and reference match; order committed |
| Payment pending | Failed | System after PSP failure or timeout | No order fulfilment started; stock released |
| Awaiting acceptance | Accepted | Supplier owner or staff | Stock confirmed; within acceptance window |
| Awaiting acceptance | Rejected | Supplier owner or staff | Reason code required; line refund initiated |
| Accepted | Preparing | Supplier | No guard beyond assignment |
| Preparing | Ready for handover | Supplier | Label generated; packing checklist complete |
| Ready for handover | Handed over | Operations or carrier | Manifest and handover evidence recorded |
| Handed over | In transit | Carrier event or operations | Tracking reference present |
| In transit | Out for delivery | Carrier event or operations | Destination hub reached |
| Out for delivery | Delivered | Carrier event or operations | POD evidence recorded |
| Out for delivery | Failed attempt | Carrier or operations | Reason code required; retry policy applied |
| Delivered | Completed | System after return window | No open return or dispute |
| Any pre-delivery | Cancelled | Customer before acceptance; operations with reason after | Refund and stock release rules apply |
| Delivered or completed | Return requested | Customer within window | Eligibility rules pass |
| Return approved | Refund pending | Support or finance | Inspection outcome recorded |
| Refund pending | Refunded | Finance and PSP | Approval threshold met; PSP confirms |
| Any | Disputed | Customer, support or finance | Dispute record opened; payout hold applied |

**Rule:** no role may set an arbitrary status directly. Every change is a command with a guard, a reason where required, and an audit event. The database should reject invalid transitions even if a user interface bug tries to make one.

## 8.5 Edge cases that must be specified before build

| Case | Required behaviour |
|---|---|
| Customer pays, then closes browser before callback | Order is created from the verified server-side status; customer receives confirmation; no duplicate order on retry |
| Duplicate payment callback | Second callback is idempotent; no duplicate ledger entry or order |
| Supplier accepts, then finds stock missing | Supplier must request cancellation with reason; customer is informed and refunded for that line; supplier scorecard records it |
| One supplier rejects, others accept | Parent order remains; rejected line refunded; delivery fee recalculated or partially refunded according to policy |
| Two parcels, one delivered, one lost | Parent shows partial delivery; lost parcel triggers carrier claim and customer remedy without freezing the delivered item's completion |
| Customer returns one item from a multi-item supplier order | Refund is calculated per line plus the applicable delivery share; commission is reversed on that line |
| Price changes after order placement | Order item snapshot is authoritative; new price applies only to future orders |
| Supplier is suspended with open orders | Open orders must be fulfilled, reassigned or cancelled under an operations runbook; payouts may be held |
| Refund after payout | Platform records a negative supplier balance or future deduction; it does not silently reduce an unrelated payout without a statement |
| Chargeback or reversal after settlement | Finance opens a case, freezes future payouts if needed, and records the loss against the responsible party where evidence supports it |

---

# 9. Business rules catalogue

The rules below are the bridge between business intent and testable requirements. **Status** shows whether the rule is confirmed by the brief, assumed from the concept, proposed here, or still open.

::: {.rules-table}
| ID | Rule | Rationale / source | Status |
|---|---|---|---|
| BR-001 | One checkout creates one parent order and one supplier order per supplier. | Customer sees one order; platform operates many (concept 7.3) | Proposed |
| BR-002 | Stock is reserved when a payment intent is created and released if payment fails or the reservation expires. | Prevents overselling without holding stock indefinitely | Proposed |
| BR-003 | Prices and totals are calculated server-side from current product and fee records; the browser total is never authoritative. | Prevents tampering and price drift | Proposed |
| BR-004 | Commission is calculated per order line on net merchandise value after line discounts and returns, not on the gross amount captured. | Honest revenue (concept 9.1) | Proposed |
| BR-005 | The customer delivery charge, the carrier charge and the platform coordination fee are recorded as separate amounts. | Prevents pass-through money being counted as revenue | Proposed |
| BR-006 | A refund may include the item value and the applicable delivery share; change-of-mind refunds may exclude delivery. | Fairness and published policy | Open |
| BR-007 | A supplier payout is held until delivery plus the return window, unless a dispute or risk flag extends the hold. | Protects customers and the platform | Proposed |
| BR-008 | A supplier cannot mark an order delivered; delivery requires carrier or operations evidence. | Separation of duties and proof | Proposed |
| BR-009 | Every financial adjustment requires a reason code, an actor and a second approver above a threshold. | Auditability and fraud control | Proposed |
| BR-010 | A product is visible only after moderation approval and while stock is above zero. | Catalogue quality and customer trust | Proposed |
| BR-011 | Placing an order snapshots the product title, SKU, price, tax line and commission rule; later edits do not change the order. | Reproducible invoices and disputes | Proposed |
| BR-012 | A customer may cancel before supplier acceptance; after acceptance, cancellation becomes a return request subject to policy. | Operational reality | Proposed |
| BR-013 | A supplier sees only the customer data required to pack and hand over: name, phone, address, landmark and order items. | Data minimisation and disintermediation control | Proposed |
| BR-014 | Reviews are accepted only from verified purchasers, one review per purchased line, and are moderated for abuse rather than disagreement. | Trust (concept 8.7) | Proposed |
| BR-015 | Prohibited items are blocked at listing and removed at moderation; a supplier that relists them is suspended. | Legal and brand risk | Proposed |
| BR-016 | Every shipment records carrier, service, waybill, cost, weight, dimensions, status events and POD. | Claims and reconciliation | Proposed |
| BR-017 | Failed delivery attempts follow a published retry policy; the customer is contacted before a second attempt. | First-attempt success and fairness | Proposed |
| BR-018 | The return window starts at delivery, not dispatch, and excludes items marked non-returnable for hygiene or safety reasons where law allows. | Consumer fairness | Open |
| BR-019 | All monetary amounts are stored as integer Tanzanian shillings; rounding rules are explicit and applied once per calculation. | Avoids floating-point money errors | Proposed |
| BR-020 | VAT and other tax lines are stored per invoice line and are configurable; the platform does not assume a tax treatment. | Tax law is unresolved | Open |
| BR-021 | The platform is not an escrow or deposit-taking service and does not hold customer funds in a platform wallet. | Regulatory boundary in the brief | Confirmed |
| BR-022 | Brand, territory, fee and approval rules are configuration with effective dates, not code branches. | Configurable franchise requirement | Confirmed |
| BR-023 | Audit records are append-only and cannot be edited or deleted through the application, including by a super administrator. | Accountability | Proposed |
| BR-024 | Personal data is collected for a stated purpose, retained only as long as needed or required, and deleted or anonymised on schedule. | PDPA and minimisation | Proposed |
| BR-025 | Marketing consent is separate from transactional messages and can be withdrawn without closing the account. | Consent quality | Proposed |
| BR-026 | Staff access to customer or supplier data outside normal duties requires a reason and is time-bound and logged. | Insider risk | Proposed |
| BR-027 | A refund cannot exceed the captured amount for the payment minus prior refunds and reversals. | Prevents over-refunding | Proposed |
| BR-028 | A payout batch requires a preparer and a different approver; the approver sees the full statement and exceptions. | Maker-checker | Proposed |
| BR-029 | A supplier with an open dispute, negative balance or unresolved KYC issue may have payouts held with a written reason. | Risk control | Proposed |
| BR-030 | Carrier and supplier performance is measured from system events, not from manual opinion, and is visible to the party concerned. | Fair scorecards | Proposed |
| BR-031 | The platform must be able to operate a shipment manually with the same records used by an API carrier. | Carrier-agnostic pilot | Confirmed |
| BR-032 | A customer can obtain a human response within the published support hours; automated replies do not close a ticket. | Trust and consumer care | Proposed |
:::

---

# 10. Non-functional requirements (draft)

## 10.1 Approach

Non-functional requirements are written as measurable statements with a verification method. Targets marked **[Proposed]** are starting points for the SRS and must be confirmed against budget, hosting choice and device evidence. They are not marketing claims.

## 10.2 Requirements

| ID | Category | Requirement | Target | Verification |
|---|---|---|---|---|
| NFR-P-01 | Performance | Customer home, category and product pages load quickly on a mid-range Android phone on 4G | Largest Contentful Paint at 75th percentile within 3.0 seconds | Lighthouse and field measurement |
| NFR-P-02 | Performance | Core read APIs respond quickly under pilot load | 95th percentile within 500 ms, excluding third-party calls | Load test with production-like data |
| NFR-P-03 | Performance | Write APIs complete predictably | 95th percentile within 1,000 ms, excluding PSP or carrier latency | Load test and tracing |
| NFR-P-04 | Performance | Search returns relevant results at pilot catalogue size | 95th percentile within 800 ms at 5,000 SKUs | Query benchmark |
| NFR-P-05 | Performance | A customer can complete checkout on a mid-range device | Median under 5 minutes including payment | Moderated usability test |
| NFR-S-01 | Scalability | The pilot supports concurrent browsing and order bursts with headroom | 100 concurrent users and 10 checkout submissions per minute, with 5x design headroom | Load test |
| NFR-S-02 | Scalability | The schema and indexes support growth without re-architecture | 10x SKUs and 5x order volume over pilot | Design review and synthetic data test |
| NFR-A-01 | Availability | Catalogue, checkout and order APIs are available during support hours | 99.5% monthly, excluding announced maintenance | Uptime monitoring |
| NFR-R-01 | Reliability | Payment and order operations survive retries without duplication | Idempotent initiation and callback; zero duplicate orders in test | Integration and chaos tests |
| NFR-R-02 | Reliability | Data can be recovered after failure | Recovery point within 15 minutes; recovery time within 4 hours | Restore drill |
| NFR-R-03 | Reliability | Background jobs retry safely and surface dead letters | At-least-once delivery with idempotent handlers; alert on failures | Job failure injection |
| NFR-SEC-01 | Security | Authentication, checkout and admin meet a recognised application security baseline | OWASP ASVS Level 2 for in-scope controls | Security review and penetration test |
| NFR-SEC-02 | Security | Traffic is encrypted and secrets are protected | TLS 1.2 or higher; secrets in managed store; no secrets in logs | Configuration review and scan |
| NFR-SEC-03 | Security | Passwords and staff authentication resist compromise | Argon2id hashing; MFA required for staff and suppliers | Code review and test |
| NFR-SEC-04 | Security | Authorisation is enforced server-side on every request | Deny-by-default; tenant scoping; automated authorisation tests for every role | Test suite and manual review |
| NFR-SEC-05 | Security | Abuse is rate-limited | Login 5 attempts per minute per IP; OTP 3 per 10 minutes per number; checkout 10 per minute per user | Configuration test |
| NFR-SEC-06 | Security | Uploads cannot become an attack vector | Type and size limits; malware scan; private storage; signed access | Upload tests |
| NFR-PRIV-01 | Privacy | Consent and privacy notices are recorded and enforceable | Versioned notice; consent per purpose; withdrawal honoured | Process and data audit |
| NFR-PRIV-02 | Privacy | Personal data is minimised in logs and interfaces | No card data; PII masked by default; access logged | Log inspection and role tests |
| NFR-PRIV-03 | Privacy | Data subject requests can be fulfilled | Export, correction and deletion workflow within the statutory period to be confirmed | Tabletop exercise with counsel |
| NFR-AUD-01 | Audit | Sensitive actions are traceable | 100% of role, refund, payout, price and supplier-status changes logged with actor, reason and before/after | Audit coverage test |
| NFR-AUD-02 | Audit | Audit records resist tampering | Append-only storage; separate access; retention per legal advice | Design review and access test |
| NFR-M-01 | Maintainability | Critical modules have automated tests | At least 70% unit coverage on order, payment, commission and refund logic; integration tests for PSP and carrier adapters | CI report |
| NFR-M-02 | Maintainability | Database changes are controlled | Versioned migrations; tested rollback; no manual production schema edits | Migration review |
| NFR-M-03 | Maintainability | Code and decisions are documented | Architecture decision records; API specification generated from source; runbooks for operations | Documentation review |
| NFR-OBS-01 | Observability | Failures are visible before customers report them | Structured logs with request IDs; error tracking; uptime and payment-success alerts; dashboards | Incident drill |
| NFR-ACC-01 | Accessibility | Critical customer flows are usable with assistive technology | WCAG 2.1 AA for catalogue, cart, checkout and order tracking | Accessibility audit |
| NFR-I18N-01 | Localisation | The interface works in Swahili and English | Swahili default; all strings externalised; TZS formatting; no hard-coded copy | Content review and pseudo-localisation test |
| NFR-COMP-01 | Compatibility | The site works on the devices customers actually use | Current Chrome, Safari, Firefox and Android WebView; graceful degradation on older devices | Device lab and analytics |
| NFR-SUP-01 | Supportability | Support can find any order quickly | Order lookup by number, phone, supplier or tracking reference in under 30 seconds | Usability test with support staff |

## 10.3 Capacity assumptions

| Dimension | Pilot assumption | Design headroom | Source |
|---|---:|---:|---|
| Registered customers | 10,000 | 50,000 | Planning assumption |
| Active suppliers | 40 | 200 | Concept Section 8.5 |
| Active SKUs | 1,200 | 12,000 | Concept Section 8.5 |
| Orders per month at month 6 | 900 | 4,500 | Concept Section 3.4 |
| Peak checkout submissions | 10 per minute | 50 per minute | Planning assumption |
| Concurrent browsing users | 100 | 500 | Planning assumption |
| Product images per SKU | 5 | 10 | Catalogue standard |
| Shipment events per parcel | 6 | 12 | Carrier process |

## 10.4 Retention and audit questions

- How long must KYC documents, invoices, payment records and audit logs be retained under Tanzanian law? **[Open — counsel and accountant]**
- Must personal data be stored in Tanzania, or is a cross-border transfer mechanism acceptable? **[Open — counsel]**
- What is the statutory timeline for responding to a data subject request and for notifying a breach? **[Open — counsel]**
- Are there sector-specific record-keeping rules for payments or courier services that apply to the marketplace? **[Open — counsel]**

Until these are answered, the design should support configurable retention, export and deletion rather than hard-coding a period.

---

# 11. Regulatory and compliance drivers

## 11.1 Caveat

This section identifies design drivers, not legal conclusions. The sources are official pages or professional summaries, and several apply to the platform only after counsel confirms the platform's role. Every row marked **[Open]** requires a written opinion or a regulator's guidance before launch.

## 11.2 Compliance register

| ID | Area | What the platform must be able to do | Why it may apply | Status / source |
|---|---|---|---|---|
| REG-01 | Data protection (PDPA 2022, PDPC) | Publish a privacy notice; record consent; honour access, correction and deletion requests; secure data; appoint a contact; register where required | The platform collects customer, supplier and KYC data | Open; S14, S15 |
| REG-02 | Consumer contracts (FCC Standard Form Regulations 2014) | Publish plain-language terms, returns and delivery policies; retain versions; give a copy at checkout; provide redress | Standard-form consumer contracts and e-commerce terms | Open; S16 |
| REG-03 | Electronic transactions (Electronic Transactions Act 2015) | Keep reliable electronic records and audit trails; support electronic acceptance and signatures where used | Orders, contracts and notices are electronic | Open; S19 |
| REG-04 | Payment services (Bank of Tanzania) | Collect and settle through an authorised provider; keep pass-through money separate from revenue; do not operate an informal escrow or wallet | The platform collects customer money and pays suppliers | Open; S6 |
| REG-05 | Courier and postal services (TCRA) | Use licensed carriers; define whether the platform is a coordinator or a carrier; keep shipment records | Parcel delivery is central to the promise | Open; S17 |
| REG-06 | VAT (TRA) | Register if threshold is met; calculate and display tax correctly; issue compliant invoices; keep records | Commission, delivery and subscription revenue may be taxable | Open; S11 |
| REG-07 | Corporate income tax (TRA) | Produce accurate revenue, cost and profit records; support filings | The operating company is taxable | Open; S12 |
| REG-08 | Company, business names and trademarks (BRELA) | Register the company and marks; record any brand licence; protect the platform name | Brand and franchise layer | Open; S13 |
| REG-09 | Fair competition | Avoid resale price maintenance and anti-competitive exclusivity; keep supplier terms transparent | Supplier agreements and promotions | Open |
| REG-10 | Consumer protection and product safety | Honour warranties and returns; remove prohibited or unsafe goods; keep evidence of supplier declarations | Customer trust and legal exposure | Open |
| REG-11 | Franchise and brand licence | Record the licence scope, territory, fees, quality controls, termination and IP ownership; do not imply a relationship that does not exist | Proposed Usiri relationship | Open; S13 |
| REG-12 | Insurance and liability | Record carrier liability terms and insurance evidence; define who bears loss, damage and injury | Parcels and products | Open |

## 11.3 Data protection requirements that affect the design

1. **Purpose limitation.** Each data field has a stated purpose. KYC data is not reused for marketing.
2. **Lawful basis.** Contract is the basis for order fulfilment; consent is the basis for marketing; legal obligation covers tax and fraud records. Counsel must confirm.
3. **Minimisation.** Suppliers and carriers receive only the fields needed to perform their task, not the whole customer record.
4. **Retention.** Retention is configurable and documented per data class. Deletion must not break financial or audit obligations.
5. **Processor agreements.** The PSP, SMS provider, cloud host, support tool and analytics provider must be bound by written data-processing terms.
6. **Security.** Encryption in transit and at rest, access control, logging and breach response are part of the compliance obligation, not only engineering good practice.
7. **Rights.** A customer can request a copy, correction or deletion of personal data through a documented process, with identity verification.
8. **Cross-border transfer.** Hosting and backup locations must be chosen with counsel, not by accident.

## 11.4 The payment and escrow boundary

The brief is explicit: the platform must not assume it holds customer funds in escrow. The design therefore separates four things:

- **Collection:** the PSP collects from the customer under the platform's merchant account.
- **Platform revenue:** commission, coordination fee and subscription, recognised when earned.
- **Supplier payable:** a contractual debt owed by the platform to the supplier after the payout hold, not a segregated customer deposit.
- **Carrier payable:** a cost owed to the carrier under its invoice.

Whether this structure requires a payment licence, a specific PSP marketplace product, or a different legal form is an **[Open]** question for counsel and the PSP. The software must not describe itself as escrow, trust account or wallet unless the legal structure supports that description.

## 11.5 Consumer terms and returns

The platform must publish, version and present at checkout:

- Terms of service and the role of the marketplace versus the supplier.
- Delivery promise, zones, fees and failed-delivery policy.
- Return and refund policy, including exclusions and who pays reverse transport.
- Warranty and product-safety position.
- Complaints and dispute process, with response times.
- Privacy notice and consent choices.

The FCC standard-form contract and consumer-protection position must be reviewed before launch. The software should store the exact policy version accepted by each customer at checkout.

## 11.6 Tax and invoicing

The platform must be able to:

- Store tax rates and tax amounts per line, with effective dates.
- Distinguish marketplace commission, delivery coordination, subscription and sponsored revenue.
- Produce a customer receipt and a supplier statement that reconcile to the ledger.
- Export data in a form the accountant can use for VAT and corporate tax filings.
- Support electronic fiscal receipt or invoicing requirements if advised.
- Handle withholding tax on franchise or royalty payments if advised.

No tax rate or treatment is hard-coded before the accountant confirms it.

## 11.7 Franchise and intellectual property

If a brand licence or franchise is agreed, the system must support:

- Licensed marks and assets with usage rules and expiry.
- Territory and channel restrictions.
- Fee and royalty records, including withholding tax treatment.
- Brand approval workflow for campaigns and storefront presentation.
- Quality and compliance reporting to the licensor.
- Termination and wind-down: export of data, removal of marks, continuity for customers.

If no licence is agreed, these capabilities remain inactive configuration. The platform must not display Usiri marks, imply endorsement or describe itself as a Usiri company.

## 11.8 Questions for counsel and the accountant

1. Does the platform's collection-and-settlement model require a payment service licence, or is it covered by the PSP's authorisation?
2. What registrations and filings apply under the PDPA, including controller or processor registration and a data protection officer?
3. Is the standard-form consumer contract registrable with the FCC, and what must be filed?
4. Does the platform need a courier or postal licence if it coordinates but does not physically carry parcels?
5. When does VAT registration apply, and how should commission, delivery and subscription revenue be treated?
6. What records must be kept for tax, how long, and in what format?
7. Are cross-border hosting and support tools permitted, and what safeguards are required?
8. What are the consumer warranty, return and refund obligations that cannot be contracted away?
9. What are the competition-law limits on supplier exclusivity, minimum pricing and promotions?
10. If a franchise or brand licence is signed, how should fees, royalties and withholding tax be documented and recorded?

---

# 12. Confirmed, assumed, proposed and open

## 12.1 Confirmed requirements and constraints

| ID | Item |
|---|---|
| C-01 | The application is a multi-vendor marketplace connecting customers, suppliers, the operator, carriers and payment providers. |
| C-02 | The founders intend to own the operating company and the technology. |
| C-03 | A franchise or brand arrangement with Usiri is proposed, not agreed. |
| C-04 | No Usiri API is assumed to exist; the logistics module must support Usiri or alternatives. |
| C-05 | The logistics design must be provider-agnostic and support manual and API modes. |
| C-06 | Franchise, branding and operating rules must be configurable. |
| C-07 | The platform does not assume it holds customer funds in escrow. |
| C-08 | Payment integration must use appropriately authorised providers. |
| C-09 | Confirmed, assumed, proposed and unresolved items must be clearly separated. |
| C-10 | The engineering work follows the document sequence and requires review before implementation. |

## 12.2 Assumptions carried from the concept

| ID | Assumption | Consequence if wrong |
|---|---|---|
| A-01 | Pilot city is Dar es Salaam. | Zones, delivery pricing and operations change |
| A-02 | Initial assortment is home, kitchen and small electrical goods in the TZS 30,000–250,000 band. | Catalogue model, attributes and delivery handling change |
| A-03 | 25–40 verified suppliers at launch. | Onboarding capacity and catalogue size change |
| A-04 | 900 completed orders in pilot month 6. | Capacity and support staffing change |
| A-05 | Commission hypothesis is 8%, tested between 6% and 12%. | Revenue model and supplier terms change |
| A-06 | Customer delivery charge is around TZS 5,000 per order. | Checkout conversion and contribution change |
| A-07 | Return window is 7 days from delivery. | Refund holds and policy text change |
| A-08 | Supplier payout after delivery plus the return window. | Cash flow and supplier willingness change |
| A-09 | Support hours are 09:00–18:00, Monday to Saturday. | SLA and staffing change |
| A-10 | A 30-day functional guarantee applies to eligible goods. | Returns and supplier terms change |
| A-11 | Logistics is manual at pilot, with API as an upgrade. | Build scope and carrier selection change |
| A-12 | Interface is Swahili-first with English. | Content and testing effort change |
| A-13 | Customer channel is a responsive web app or PWA. | Native app scope appears |
| A-14 | MVP build is 8–12 weeks with a dedicated technical lead and one developer. | Timeline and cost change |
| A-15 | One legal entity operates the marketplace and holds the contracts. | Multi-entity settlement and tax change |

## 12.3 Proposed design decisions

| ID | Proposal | Where it appears |
|---|---|---|
| P-01 | Parent order plus supplier orders plus shipments plus order items. | Section 8 |
| P-02 | Separate payment, fulfilment, return and dispute state dimensions. | Section 8.3 |
| P-03 | Double-entry ledger for all money movements. | Section 7.3 |
| P-04 | Role-based access with tenant scoping and field masking. | Section 5 |
| P-05 | Carrier adapter with capability discovery and manual fallback. | Section 7.5 |
| P-06 | Payment confirmation only from verified PSP callbacks and server-side status. | Section 7.3 |
| P-07 | Maker-checker for payouts, refunds above threshold and role changes. | Section 5.5 |
| P-08 | Catalogue moderation before publication and stock suppression at zero. | Section 9 |
| P-09 | Verified-buyer reviews only. | Section 9 |
| P-10 | Documentation packs and stage gates before implementation. | Section 17 |

## 12.4 Open items

| ID | Open item | Owner | Needed by |
|---|---|---|---|
| O-01 | Franchise fee, royalty, territory, term, termination and brand assets | Founders and counsel | Before any brand commitment |
| O-02 | Domain name, trademark search and brand ownership | Founders and counsel | Before public launch |
| O-03 | PSP selection, fees, settlement product and contract | Finance lead | Before payment build |
| O-04 | Carrier selection, rates, liability, insurance and API capability | Operations lead | Before logistics build |
| O-05 | Final commission, subscription and delivery pricing | Founders after supplier research | Before supplier contracts |
| O-06 | Cash on delivery: offered or not | Founders and finance | Before checkout design freeze |
| O-07 | Return window and exclusions | Founders, counsel and suppliers | Before policy publication |
| O-08 | Payout cadence and hold period | Finance and suppliers | Before settlement build |
| O-09 | VAT, invoicing and withholding treatment | Accountant | Before ledger finalisation |
| O-10 | PDPA registration, DPO and cross-border transfer position | Counsel | Before production data |
| O-11 | FCC filing and consumer terms | Counsel | Before launch |
| O-12 | Courier licensing position | Counsel | Before carrier contracts |
| O-13 | Support hours, channels and SLA | Operations | Before pilot |
| O-14 | Hosting region, budget and vendor | CTO and founders | Before architecture sign-off |
| O-15 | Team skills, hiring and outsourcing | Founders | Before roadmap commitment |
| O-16 | Launch date and pilot supplier cohort | Founders and operations | Before Phase 2 gate |

---

# 13. Missing information and discovery plan

## 13.1 Evidence gaps

::: {.gaps-table}
| ID | Missing information | Why it matters | How to obtain it | Impact if unresolved |
|---|---|---|---|---|
| GAP-01 | Customer willingness to pay a delivery fee and buy these categories online | Determines whether demand exists at the modelled price | 30 interviews, 150 survey responses, 8 mystery shops | No defensible demand case; checkout and pricing assumptions are guesses |
| GAP-02 | Supplier willingness to accept commission, subscription and service standards | Determines supply and unit economics | 15 interviews, 5 site visits, written indications | Commission and catalogue plan cannot be set; suppliers may refuse |
| GAP-03 | Carrier rates, transit times, liability and API capability | Determines delivery cost, promise and integration mode | Three written quotations, sample shipments, terms review | Delivery promise cannot be costed; manual process may be the only option |
| GAP-04 | PSP merchant terms, fees, settlement and refund capabilities | Determines payment architecture and cash flow | Two proposals, sandbox tests, contract review | Payment build cannot start; settlement model may not be supported |
| GAP-05 | Franchise or brand terms | Determines branding, fees and approval workflow | Written term sheet and counsel review | Brand configuration remains speculative; no marks may be used |
| GAP-06 | Legal position on payments, data, consumer contracts and courier coordination | Determines whether the model can operate as designed | Written counsel memo | Launch may be blocked or require redesign |
| GAP-07 | Tax treatment and invoicing requirements | Determines ledger, receipts and reporting | Accountant ruling | Incorrect invoices and tax filings; retrofit cost |
| GAP-08 | KYC document standard and verification process | Determines supplier onboarding and fraud control | Counsel and compliance adviser | Weak supplier verification; regulatory and fraud exposure |
| GAP-09 | Market return and warranty norms | Determines policy and refund reserves | Competitor policy review, supplier interviews | Return rate and contribution assumptions may be wrong |
| GAP-10 | Address quality and last-mile practice | Determines zone design, failed-delivery rate and support load | 50 address tests, carrier data, field observation | Delivery promise and cost may be unrealistic |
| GAP-11 | Device, browser and network profile of target customers | Determines performance budget and front-end choices | Landing-page analytics, TCRA data, usability tests | Performance targets may be wrong; exclusion of low-end users |
| GAP-12 | Supplier photography and content capacity | Determines catalogue quality and moderation load | Supplier audit, sample content | Poor listings, high returns, moderation bottleneck |
| GAP-13 | Support contact volume and handling time | Determines staffing and SLA | Pilot time-and-motion, competitor benchmarks | Understaffed support; broken promise |
| GAP-14 | Insurance and liability cover | Determines who bears loss, damage and injury | Broker quotations and carrier terms | Uninsured exposure; disputes with carriers |
| GAP-15 | Hosting and data residency options | Determines architecture and compliance | Cloud proposals, counsel advice | Late re-platforming or compliance breach |
| GAP-16 | Startup and operating budget, runway | Determines scope, team and timeline | Founders' financial plan and workbook | Roadmap is unaffordable; key work stops |
| GAP-17 | Team skills and availability | Determines build versus buy and timeline | Skills audit, references, trial task | Missed milestones; poor code quality |
| GAP-18 | Brand and trademark availability | Determines name, domain and legal exposure | BRELA search and counsel | Rebranding after launch; infringement risk |
:::

## 13.2 Evidence standards

| Evidence | Minimum standard | Who owns it |
|---|---|---|
| Customer demand | 30 recorded interviews, 150 survey responses, 8 mystery shops with screenshots and timestamps | Research lead |
| Supplier supply | 15 interviews, 5 site visits, product and price lists, written indication of commission acceptance | Research lead and operations |
| Carrier capability | 3 written quotations, rate cards, sample shipment results, liability and insurance terms | Operations lead |
| Payment capability | 2 written PSP proposals, sandbox test results, settlement and refund terms | Finance lead |
| Legal and tax | Written counsel memo and accountant ruling on the questions in Section 11.8 | Founders |
| Franchise | Written term sheet or a clear written decline | Founders |
| Technical feasibility | Spike of the riskiest integration, not a full build | CTO |

## 13.3 Research sequence

1. **Legal and payment boundary first.** If the collection-and-settlement model cannot be lawfully operated with an available PSP, the product design changes fundamentally. Do this before UI work.
2. **Carrier and supplier quotes second.** These determine delivery cost, promise and catalogue scope.
3. **Customer demand third.** Willingness to pay is tested with a landing page and interviews, not with a full build.
4. **Franchise conversation only when the evidence pack is ready.** Do not approach Usiri with an unfunded idea and no operating plan.
5. **Architecture spike last.** Prove the PSP callback, the multi-supplier order split and the carrier adapter with a thin technical spike, not a full application.

## 13.4 What must not be built yet

- A production checkout before the PSP and legal structure are confirmed.
- A carrier integration before a carrier agreement and API documentation exist.
- A franchise-branded interface before a written licence exists.
- A supplier payout engine before the settlement and tax treatment are confirmed.
- A native app before the web pilot proves demand.
- A recommendation engine, wallet or loyalty scheme before there is data and a licensed model.

---

# 14. Decisions required from the founders

The first four decisions blocked the BRD and SRS; they were answered on 30 October 2026 and are marked below. The rest can be resolved during requirements elaboration, but each has a default so that work is not stalled.

::: {.dec-table}
| ID | Decision | Options and recommended default | Impact | Status |
|---|---|---|---|---|
| DEC-01 | Launch scope | **Recommended:** Dar es Salaam, home, kitchen and small electrical goods, TZS 30,000–250,000, 25–40 suppliers. Alternatives: broader general merchandise, electronics-first, multi-city | Sets catalogue, delivery, supplier and compliance scope | **Decided 30 Oct 2026 — general merchandise**, six bounded departments, 40 suppliers, 800–1,200 SKUs. Recommendation not taken; see UM-AMD-001 |
| DEC-02 | Fulfilment model | **Recommended:** supplier-held stock, platform-coordinated pickup or drop-off, no warehouse or fleet. Alternatives: marketplace hub, supplier self-delivery, dropship | Sets logistics module, cost and control | **Decided 30 Oct 2026 — as recommended** |
| DEC-03 | Payment and settlement | **Recommended:** licensed PSP collects; platform settles suppliers after delivery plus return window, with holds and maker-checker. Alternatives: split settlement at capture, cash on delivery, hybrid | Sets payment architecture, cash flow and legal review | **Decided 30 Oct 2026 — as recommended** |
| DEC-04 | Build route | **Recommended:** custom modular monolith (Next.js, FastAPI, PostgreSQL) with an 8–12 week MVP and a dedicated technical lead. Alternatives: hosted marketplace first, hybrid, longer part-time build | Sets budget, team, timeline and control | **Decided 30 Oct 2026 — as recommended; 8–12 weeks recorded as a stretch target, with a week-8 scope gate** |
| DEC-05 | Order structure | **Recommended:** parent order plus supplier orders plus shipments plus items | Determines the core data model and all financial logic | Proposed; confirm in SRS |
| DEC-06 | State model | **Recommended:** separate payment, fulfilment, return and dispute dimensions, with a derived customer summary | Prevents an unmanageable single status enum | Proposed; confirm in SRS |
| DEC-07 | Commission and fees | Start with the 8% hypothesis, configurable and effective-dated; final rate after supplier research | Revenue and supplier contracts | Open; resolve before contracts |
| DEC-08 | Return and payout policy | 7-day return window; payout after delivery plus window; exceptions for disputes | Cash flow, policy text and customer trust | Open; resolve before build freeze |
| DEC-09 | Logistics mode | Manual Mode A at pilot; adapter contract designed now; API only with a capable carrier | Build scope and carrier dependency | Proposed; confirm |
| DEC-10 | Brand and franchise configuration | Build the configuration capability but keep it inactive until a written licence exists | Prevents implied affiliation and rework | Confirmed direction |
| DEC-11 | Hosting and data location | Managed cloud with a region chosen after counsel advice; no hard-coded vendor | Compliance, cost and operations | Open; resolve before architecture |
| DEC-12 | Language and support | Swahili default, English available; support 09:00–18:00 Monday to Saturday at pilot | Content, staffing and SLA | Proposed; confirm |
:::

## 14.1 Status of the decisions after 30 October 2026

DEC-01 to DEC-04 are closed. Closing DEC-01 created eight sub-decisions, D-13 to D-20, recorded in the decision log and the amendment: the exact department tree, the minimum delivered basket, the category commission schedule, beauty authenticity evidence, baby safety declaration, the fashion return policy, the launch supplier cohort, and the timeline fallback. Four of them — D-16, D-17, D-18 and D-20 — must be answered before the related category goes live or before the week-8 gate. None blocks starting the BRD.

## 14.2 Decision process

1. Founders read this report and the concept document.
2. Each founder records an independent view on DEC-01 to DEC-04 before the meeting.
3. The group discusses differences, not preferences, and records the decision, the reason and the dissent in the decision log.
4. A decision is not final until its evidence implications are accepted. For example, choosing a PSP is not a decision to integrate before counsel confirms the model.
5. Decisions are versioned. A later change requires a new entry, not a silent edit.

---

# 15. Initial delivery risk register

Scores use likelihood 1–5 and impact 1–5; the score is the product. These are planning assessments, not measured probabilities.

| ID | Risk | Likelihood | Impact | Score | Mitigation | Trigger |
|---|---|---:|---:|---:|---|---|
| RSK-01 | Scope creep turns the MVP into a full marketplace | 4 | 4 | 16 | Strict scope rule; change board; defer list | New feature requested without a pilot-order justification |
| RSK-02 | PSP onboarding or integration takes longer than planned | 4 | 4 | 16 | Start PSP conversations before build; sandbox spike; alternative provider identified | No sandbox access within two weeks |
| RSK-03 | Carrier cannot provide rates, tracking or liability terms | 4 | 4 | 16 | Manual mode by default; qualify a second carrier; written terms before pilot | No rate card or tracking sample by Phase 2 |
| RSK-04 | Multi-supplier order logic is underestimated | 3 | 5 | 15 | Design parent/sub-order model first; test partial acceptance and partial refund | First sprint cannot model a three-supplier order |
| RSK-05 | Payment reconciliation errors create supplier distrust | 3 | 5 | 15 | Double-entry ledger; daily reconciliation; exception queue; finance sign-off | More than 0.5% unmatched transactions in test |
| RSK-06 | Personal data breach or unlawful processing | 3 | 5 | 15 | PDPA review; minimisation; encryption; access control; incident plan | Any confirmed unauthorised access |
| RSK-07 | Regulatory position blocks the payment or courier model | 3 | 5 | 15 | Counsel memo before build; PSP guidance; fallback model | Counsel identifies a licensing requirement not covered by the PSP |
| RSK-08 | Key-person dependency on one developer | 4 | 4 | 16 | Documentation; code review; second contributor; repository access | One person holds all production access |
| RSK-09 | Suppliers do not adopt the portal or keep stock accurate | 4 | 4 | 16 | Simple onboarding; CSV upload; WhatsApp support; stock audits; scorecard | Fewer than 60% of suppliers update stock weekly in pilot |
| RSK-10 | Cost overrun exhausts the pilot budget | 3 | 4 | 12 | Lean scope; fixed-price where possible; monthly burn review; stop rules | Burn exceeds plan by 20% for two months |
| RSK-11 | Franchise dependency distorts priorities or brand use | 3 | 3 | 9 | No dependency in critical path; written licence only; fallback brand | Team waits for Usiri instead of testing demand |
| RSK-12 | Support volume overwhelms the small team | 3 | 4 | 12 | Self-service order tracking; canned responses; SLA triage; exception codes | More than 20% of orders generate a ticket |
| RSK-13 | Payment fraud or friendly fraud | 3 | 4 | 12 | PSP risk tools; velocity limits; verified delivery; evidence for disputes | Chargeback rate above 1% of transactions |
| RSK-14 | Address and delivery failures damage the promise | 4 | 3 | 12 | Landmark capture; phone confirmation; zone design; second attempt | First-attempt success below 70% for two weeks |
| RSK-15 | Poor performance on low-end devices | 3 | 3 | 9 | Performance budget; image optimisation; device testing; CDN | LCP above 4 seconds on target devices |

---

# 16. Traceability seed

## 16.1 Objective-to-capability trace

| Objective | Capabilities | Key rules | Quality attributes | Acceptance theme | Evidence |
|---|---|---|---|---|---|
| OBJ-01 Demand | CAP-05, CAP-06, CAP-07 | BR-001, BR-002, BR-003, BR-011 | NFR-P-01, NFR-P-04, NFR-P-05 | A customer can buy from three suppliers in one checkout | Pilot orders, conversion |
| OBJ-02 Delivery | CAP-10 | BR-016, BR-017, BR-030 | NFR-A-01, NFR-R-02 | Every parcel has a carrier, waybill, status history and POD | On-time delivery, first-attempt success |
| OBJ-03 Trust | CAP-11, CAP-12 | BR-006, BR-009, BR-014, BR-032 | NFR-AUD-01, NFR-PRIV-01 | A return is resolved with a refund and a customer communication | Resolution time, CSAT, return rate |
| OBJ-04 Supply | CAP-01, CAP-02, CAP-03 | BR-010, BR-015, BR-029 | NFR-SEC-04, NFR-PRIV-02 | A supplier is verified, approved, publishes approved products and sees only its own data | Suppliers onboarded, retention |
| OBJ-05 Economics | CAP-08, CAP-09, CAP-15 | BR-004, BR-005, BR-007, BR-027 | NFR-M-01, NFR-R-01 | Commission, refunds and payouts reconcile to the ledger | Contribution margin, reconciliation rate |
| OBJ-06 Compliance | CAP-01, CAP-14 | BR-020, BR-021, BR-024, BR-025 | NFR-PRIV-01, NFR-AUD-02 | The platform can evidence consent, terms version, invoices and audit | Legal review, filings |
| OBJ-07 Operability | CAP-12, CAP-14, CAP-15 | BR-009, BR-023, BR-028 | NFR-OBS-01, NFR-SUP-01 | The team can run a pilot day without shadow spreadsheets | Orders handled in system |
| OBJ-08 Scale decision | CAP-15, CAP-17 | BR-019, BR-030 | NFR-S-01, NFR-S-02 | Reports show demand, retention, delivery and unit economics by cohort | Month-6 review pack |

## 16.2 How traceability will be maintained

- Every requirement in the SRS will carry an ID such as `REQ-ORD-014`.
- Every requirement will reference at least one objective and one acceptance test.
- Every business rule will be enforced in code, configuration or process, with a test or control evidence.
- Every test case will reference the requirement it proves.
- The matrix will be a living file, reviewed at each stage gate. A requirement without a test is not complete; a test without a requirement is either unnecessary or reveals a missing requirement.

---

# 17. Document roadmap and phase gates

## 17.1 Document packs

| Pack | Documents | Purpose | Gate |
|---|---|---|---|
| **0. Discovery** | This report; decision log; traceability seed | Establish scope, actors, rules and unknowns | G0 scope approval |
| **A. Business** | BRD; stakeholder and role matrix; functional requirements catalogue; use cases; user stories and acceptance criteria | Define what the business needs, in testable language | G1 requirements sign-off |
| **B. Technical** | SRS; non-functional requirements catalogue; system architecture; database design; API specification; security architecture | Define how the system will be built and controlled | G2 architecture and security review |
| **C. Experience** | UI/UX specification; wireframes and prototype; design system; content and localisation guide | Define every major screen and interaction | G3 prototype review |
| **D. Integration** | Payment integration specification; logistics integration specification; notification specification | Define external contracts and failure handling | G3 with Pack B |
| **E. Delivery** | Testing and QA plan; DevOps and deployment plan; backup and disaster recovery plan; development roadmap; MVP scope; project risk register | Define how the build is delivered and verified | G4 build readiness |
| **F. Implementation** | Code, environments, migrations, runbooks, training and pilot operations | Build, test and launch | G5 pilot go/no-go |

The 20 documents named in the brief are distributed across these packs. Several are combined where splitting them would create duplication without adding clarity; the intent of the brief is coverage, not bureaucratic count.

## 17.2 Stage gates

| Gate | Entry criteria | Exit criteria | Who decides |
|---|---|---|---|
| G0 Scope | This report complete; founders have read it | DEC-01 to DEC-04 answered; scope boundary accepted | Founders |
| G1 Requirements | Discovery decisions recorded; evidence gaps have owners | BRD and SRS reviewed; traceability complete for MVP; no unresolved blocking rule | Founders and product owner |
| G2 Architecture | SRS baseline; PSP and carrier constraints known | Data model, API, security and deployment reviewed; risks accepted | CTO, founders, external reviewer |
| G3 Experience | Architecture baseline; content plan | Prototype tested with target users; accessibility and localisation checked | Product owner and design lead |
| G4 Build readiness | Architecture and UX approved; team and budget confirmed | Test plan, environments, CI/CD, backup and runbooks ready | CTO and founders |
| G5 Pilot launch | MVP acceptance criteria met; legal baseline in place; suppliers and carrier ready | Controlled pilot begins with a stop rule | Founders |

## 17.3 Rules

- No production code before G2 and G3 approval. A technical spike is allowed to test a risk, but it is not a product.
- No brand use before a written licence.
- No live payment collection before PSP onboarding and legal review.
- No customer data in production before the privacy notice, retention plan and access controls are in place.
- Any scope change after G1 goes through the change log with cost, risk and schedule impact.
- A decision may be reversed, but only with a new decision-log entry explaining why.

## 17.4 Immediate next step

After the four blocking decisions are answered, the next document is the **BRD**, followed by the **SRS**. The BRD will restate the business objectives and scope in business language; the SRS will convert the capability map, business rules and non-functional requirements into numbered, testable requirements with use cases and acceptance criteria.

---

# 18. Questions for this review round

The questions are deliberately grouped and limited. Each has a recommended default so that the discussion starts from a concrete proposal rather than a blank page.

> **Answered 30 October 2026.** All four groups were put to the founders and answered. The answers are recorded in full in `01_Decision_Log.md` v0.2 and elaborated in `03_Decision_Outcome_and_Scope_Amendment.md` v1.0. The options below are retained as the record of what was considered.
>
> | Group | Question | Answer |
> |---|---|---|
> | 1 | What may the first release sell, where, and to how many suppliers? | **General merchandise**, bounded to six departments in Dar es Salaam; 40 suppliers; 800–1,200 SKUs. The recommendation was not taken. |
> | 2 | Who holds stock and who moves the parcel? | **Supplier-held stock, platform-coordinated licensed carriers.** As recommended. |
> | 3 | How is money collected and when are suppliers paid? | **Licensed PSP collects; supplier payout after delivery plus the return window.** As recommended. |
> | 4 | How is it built, by whom, and in what time? | **Custom modular monolith, technical lead plus one developer, 8–12 weeks** recorded as a stretch target. As recommended, with a week-8 scope gate. |

## 18.1 Group 1: Launch scope

**Question:** What is the first release allowed to sell, where, and to how many suppliers?

- **Recommended:** Dar es Salaam mainland, home, kitchen and small electrical goods in the TZS 30,000–250,000 band, 25–40 verified suppliers. It matches the concept's evidence, keeps delivery and returns manageable, and gives a coherent reason to visit the site.
- **Alternative A:** Broader general merchandise. It increases choice but dilutes curation, raises return and counterfeit risk, and makes delivery economics harder to predict.
- **Alternative B:** Electronics first. It raises average order value but adds warranty, theft, counterfeit and price-transparency risk before operations are stable.
- **Alternative C:** Multi-city launch. It multiplies operational complexity before the Dar es Salaam promise is proven.

**Why it matters:** the category determines the product data model, delivery handling, return policy, supplier profile and marketing message. It is expensive to change after the catalogue and supplier agreements exist.

## 18.2 Group 2: Fulfilment model

**Question:** Who holds the stock, and who moves the parcel?

- **Recommended:** suppliers hold their own stock; the platform coordinates pickup or drop-off through licensed carriers; no warehouse and no fleet. This preserves the asset-light model and keeps capital within reach.
- **Alternative A:** a marketplace collection hub or dark store. It improves consolidation and control but adds rent, staffing, inventory risk and a new operating location.
- **Alternative B:** supplier self-delivery with platform tracking only. It is cheaper to start but makes the delivery promise inconsistent and hard to enforce.
- **Alternative C:** dropship direct from supplier to customer. It is fast to launch but weakens quality control and the customer experience.

**Why it matters:** the choice determines the logistics data model, who is liable when a parcel is late or damaged, and whether the platform can promise a consistent delivery window.

## 18.3 Group 3: Payment and settlement

**Question:** How is money collected, and when are suppliers paid?

- **Recommended:** a licensed PSP collects the full order amount; the platform records the supplier payable and settles after delivery plus the return window, with holds for disputes and maker-checker approval. This is the clearest boundary between customer money, platform revenue and supplier debt.
- **Alternative A:** split settlement at payment capture, if the PSP supports it. It speeds supplier payment but reduces the platform's ability to handle returns and disputes.
- **Alternative B:** cash on delivery, with commission invoiced to suppliers. It serves customers without mobile money but creates collection, reconciliation and fraud risk.
- **Alternative C:** a hybrid, with prepaid PSP payment as the default and cash on delivery in selected zones. It adds a second money workflow and must not be attempted before the prepaid flow is stable.

**Why it matters:** it determines the payment integration, ledger, refund process, supplier contract and legal review. It cannot be left to the build team to infer.

## 18.4 Group 4: Build route

**Question:** How should the first release be built, and with what team and timeline?

- **Recommended:** a custom modular monolith using Next.js, TypeScript, FastAPI and PostgreSQL, with a dedicated technical lead, one developer and a part-time designer, delivered in 8–12 weeks. It gives control over the multi-supplier order, settlement and carrier adapter, which are the differentiating parts.
- **Alternative A:** a hosted marketplace platform first, customised through plugins. It is faster to a storefront but constrains the order, payout and logistics logic and may add transaction fees.
- **Alternative B:** a hybrid, buying the storefront and payments while building the supplier portal and delivery orchestration. It balances speed and control but creates two systems to integrate.
- **Alternative C:** the same custom build over 16–20 weeks with a part-time team. It reduces cash burn per month but delays learning and increases the risk that the market moves first.

**Why it matters:** it sets the budget, the hiring plan, the architecture and the amount of custom control over the marketplace's core differentiators.

## 18.5 After the answers

The answers are recorded in `01_Decision_Log.md` v0.2. The scope consequence is issued as UM-AMD-001 and governs over the scope recommendation in Section 3. The remaining open items are D-13 to D-20 in the amendment, which must be resolved before the relevant part of the BRD, SRS or category go-live. The BRD and SRS are drafted against the amended scope. No code will be written until the architecture and UX packs are reviewed and approved.

---

# Appendix A. Glossary

| Term | Meaning in this document |
|---|---|
| **Parent order** | The customer's single commercial order created by one checkout, which may contain several supplier orders |
| **Supplier order (sub-order)** | The part of a parent order fulfilled by one supplier; the unit for commission, payout and supplier status |
| **Shipment** | A physical parcel or consignment with a carrier, waybill, weight and proof of delivery |
| **GMV** | Gross merchandise value: the value of goods sold before deductions |
| **Net merchandise value** | Merchandise value after line discounts and returns, before delivery and fees |
| **Take rate** | Marketplace revenue divided by gross merchandise value |
| **Contribution** | Revenue minus variable costs, before fixed operating costs |
| **PSP** | Payment service provider authorised to collect and settle payments |
| **POD** | Proof of delivery: photo, signature, code or carrier confirmation |
| **KYC** | Know-your-customer checks on a supplier's identity, ownership and payout account |
| **RBAC** | Role-based access control |
| **Maker-checker** | A control where one person prepares an action and a different person approves it |
| **Idempotency** | The property that repeating the same request does not duplicate the effect |
| **Ledger** | The record of every money movement and its allocation to accounts |
| **Reconciliation** | Matching the platform's records to the PSP or carrier statement |
| **SLA** | Service-level agreement or target for response, dispatch or resolution |
| **PDPA** | Tanzania's Personal Data Protection Act 2022 |
| **PDPC** | Personal Data Protection Commission |
| **FCC** | Fair Competition Commission |
| **TRA** | Tanzania Revenue Authority |
| **BRELA** | Business Registrations and Licensing Agency |
| **TCRA** | Tanzania Communications Regulatory Authority |
| **BoT** | Bank of Tanzania |

---

# Appendix B. Source register

This is a subset of the concept document's source register, repeated for the regulatory and partner claims used here. All sources were accessed on 29 October 2026. A source's presence does not mean it has been independently audited.

| ID | Publisher | Document | URL | Used for | Limitation |
|---|---|---|---|---|---|
| S1 | Usiri Group of Companies | About | https://www.usirigroup.co.tz/about | Self-reported years, routes, agents | Marketing claim; not audited |
| S2 | Usiri Group of Companies | Transportation | https://www.usirigroup.co.tz/services/transportation | Service scope and routes | No rates, API or liability terms |
| S4 | Usiri Group of Companies | Tracking | https://www.usirigroup.co.tz/track | Public tracking test | Returned HTTP 404 at review |
| S6 | Bank of Tanzania | National Payment Systems Annual Report 2025 | https://www.bot.go.tz/Publications/Regular/Annual%20Report/en/2026060211494565.pdf | Mobile money and licensed providers | Official; definitions differ from other sources |
| S11 | TRA | Value Added Tax | https://www.tra.go.tz/page/value-added-tax-vat | VAT rate and threshold | Official guidance; confirm current application |
| S12 | PwC | Tanzania — Taxes on corporate income | https://taxsummaries.pwc.com/tanzania/corporate/taxes-on-corporate-income | Corporate income tax | Professional summary; confirm Finance Act |
| S13 | ZATRA | Franchising Tanzania: Law, Tax and Royalty Guide | https://www.zatra.co/post/franchising-tanzania | Franchise law and tax context | Law-firm commentary; not legal advice |
| S14 | DLA Piper | Data protection laws in Tanzania | https://www.dlapiperdataprotection.com/?c=TZ&t=l | PDPA 2022 obligations | Professional summary; verify against the Act |
| S15 | Rex Attorneys | PDPC registration deadline | https://rexattorneys.co.tz/portfolio/reminder-to-clients-final-deadline-for-registration-with-the-personal-data-protection-commission-pdpc/ | PDPC registration and DPO context | Law-firm update; confirm with PDPC |
| S16 | Fair Competition Commission | Standard Form (Consumer Contracts) Regulations 2014 | https://www.fcc.go.tz/attachments/attachment-1719186970334-2762257834.%20Standard%20Form%20CONSUMER%20CONTRACTS%20Regulations%202014.pdf | Consumer contract registration | Regulation; confirm filing practice |
| S17 | TCRA | Postal services and licensing | https://www.tcra.go.tz/resources/postal-services | Courier licence categories | Official; applicability to marketplace to confirm |
| S18 | TCRA | National Addressing and Postcode | https://www.tcra.go.tz/services/featured/national-adressing-and-postcode | Address quality context | Official; practical address data remains a constraint |
| S19 | Ministry of Finance | Electronic Transactions Act 2015 (Cap. 442 R.E. 2022) | https://www.mof.go.tz/uploads/documents/en-1676545044-THE%20ELECTRONIC%20TRANSACTIONS%20ACT,%20CAP%20442%20R.E.%202022.pdf | Electronic records and signatures | Primary legislation; interpretation requires counsel |

**Software standards referenced as targets, not certifications:** OWASP Application Security Verification Standard (ASVS) Level 2 and WCAG 2.1 AA. They are used to make security and accessibility requirements testable; no audit or certification has been obtained.

---

# Appendix C. Document conventions

| Convention | Use |
|---|---|
| **OBJ-nn** | Business objective |
| **STK-nn** | Stakeholder |
| **ROL-nn** | Role |
| **CAP-nn** | Capability or module |
| **WF-nn** | End-to-end workflow |
| **BR-nnn** | Business rule |
| **NFR-xxx-nn** | Non-functional requirement |
| **REG-nn** | Regulatory or compliance driver |
| **C-nn / A-nn / P-nn / O-nn** | Confirmed, assumed, proposed, open |
| **GAP-nn** | Missing information or evidence gap |
| **DEC-nn** | Decision required |
| **RSK-nn** | Delivery risk |
| **REQ-xxx-nnn** | Requirement in the SRS, assigned later |
| **AT-nn** | Acceptance test theme, expanded in the test plan |

All monetary figures in this report are Tanzanian shillings unless stated otherwise. All dates are 2026 unless stated otherwise. Any figure described as a target is a hypothesis until measured.
